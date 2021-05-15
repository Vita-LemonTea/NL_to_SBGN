# Import necessary packages
import scispacy
import spacy
from nltk.corpus import wordnet

import libsbgnpy.libsbgn as libsbgn
from libsbgnpy.libsbgnTypes import Language, GlyphClass, ArcClass, Orientation

import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--text",
                help="biochemical process description text")
ap.add_argument("-p", "--path",
                help="path to the description text")
args = vars(ap.parse_args())

if not args.get("path", False):
    text = args["text"]

else:
    with open(args["path"], "r") as f:
        text = f.read()


# Load the NLP model
nlp = spacy.load("en_ner_bionlp13cg_md")

# Apply NLP model
doc = nlp(text)

# Examine the entities extracted by the mention detector.
print(list(doc.ents))

# Extract entities from doc
ent_bc = {}
for x in doc.ents:
    ent_bc[x.text] = x.label_

print(ent_bc)

# Extract verbs from doc
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

# create empty sbgn
sbgn = libsbgn.sbgn()

# create map, set language and set in sbgn
map = libsbgn.map()
map.set_language(Language.PD)
sbgn.set_map(map)

# create a bounding box for the map
box = libsbgn.bbox(x=0, y=0, w=363, h=253)
map.set_bbox(box)

# create glyphs
gn = 1
ent_dic = {}
for a in ent_bc:
    if ent_bc[a] == "SIMPLE_CHEMICAL":
        sbgn_glyph = GlyphClass.SIMPLE_CHEMICAL
    elif ent_bc[a] == "GENE_OR_GENE_PRODUCT":
        sbgn_glyph = GlyphClass.MACROMOLECULE
    else:
        sbgn_glyph = GlyphClass.ENTITY

    # entities and their IDs
    ent_dic[a] = 'glyph'+str(gn)

    g = libsbgn.glyph(class_=sbgn_glyph, id='glyph'+str(gn))
    g.set_label(libsbgn.label(text=a))
    g.set_bbox(libsbgn.bbox(x=40, y=120, w=60, h=60))
    map.add_glyph(g)

    gn = gn + 1

print(ent_dic)
# Dependency extraction and create arcs
sentences = list(doc.sents)
pn = 1
an = 1
for sentence in sentences:
    root_token = sentence.root

    # glyph with ports (process)
    g = libsbgn.glyph(class_=GlyphClass.PROCESS, id='pn'+str(pn),
                      orientation=Orientation.HORIZONTAL)
    g.set_bbox(libsbgn.bbox(x=148, y=168, w=24, h=24))
    g.add_port(libsbgn.port(x=136, y=180, id='pn'+str(pn)+'.1'))
    g.add_port(libsbgn.port(x=184, y=180, id='pn'+str(pn)+'.2'))
    map.add_glyph(g)


    subj = []
    obj = []
    apd = []
    for child in root_token.children:
        if child.dep_ == 'nsubj':
            subj.append(child)
            for subchild in child.children:
                if subchild.dep_ == 'conj':
                    subj.append(subchild)
        if child.dep_ == 'dobj':
            obj.append(child)
            for subchild in child.children:
                if subchild.dep_ == 'conj':
                    obj.append(subchild)
                if subchild.dep_ == 'acl:relcl':
                    apd_arc = subchild
                    for subsubchild in subchild.children:
                        if subsubchild.dep_ == 'nmod':
                            apd.append(subsubchild)


    synonyms = []
    apd_synonyms = []
    arc_names = ['consume', 'produce', 'modulate', 'stimulate', 'catalyze', 'inhibit']
    arc_dic = {'consume': ArcClass.CONSUMPTION,
               'produce': ArcClass.PRODUCTION,
               'modulate': ArcClass.MODULATION,
               'stimulate': ArcClass.STIMULATION,
               'catalyze': ArcClass.CATALYSIS,
               'inhibit': ArcClass.INHIBITION}

    for syn in wordnet.synsets(str(root_token)):
        for l in syn.lemmas():
            synonyms.append(l.name())

    arc_name = list(set(synonyms).intersection(set(arc_names)))

    if arc_name:
        sbgn_arc = arc_dic[arc_name[0]]
    else:
        sbgn_arc = ArcClass.UNKNOWN_INFLUENCE


    if sbgn_arc == ArcClass.PRODUCTION:
        sub_subgn_arc = ArcClass.CONSUMPTION
    else:
        sub_subgn_arc = sbgn_arc


    for syn in wordnet.synsets(str(apd_arc)):
        for l in syn.lemmas():
            apd_synonyms.append(l.name())

    apd_arc_name = list(set(apd_synonyms).intersection(set(arc_names)))

    if apd_arc_name:
        apd_sbgn_arc = arc_dic[apd_arc_name[0]]
        print(pn)
        print(apd_arc_name[0])
    else:
        apd_sbgn_arc = ArcClass.UNKNOWN_INFLUENCE

    for sub in subj:
        a = libsbgn.arc(class_=sub_subgn_arc, source=ent_dic[str(sub)], target='pn'+str(pn)+'.1', id="a" + str(an))
        a.set_start(libsbgn.startType(x=98, y=160))
        a.set_end(libsbgn.endType(x=136, y=180))
        map.add_arc(a)
        an = an + 1

    for ob in obj:
        a = libsbgn.arc(class_=sbgn_arc, source='pn'+str(pn)+'.2', target=ent_dic[str(ob)], id="a" + str(an))
        a.set_start(libsbgn.startType(x=98, y=160))
        a.set_end(libsbgn.endType(x=136, y=180))
        map.add_arc(a)
        an = an + 1

    for ap in apd:
        a = libsbgn.arc(class_=apd_sbgn_arc, source=ent_dic[str(ap)], target='pn'+str(pn), id="a" + str(an))
        a.set_start(libsbgn.startType(x=98, y=160))
        a.set_end(libsbgn.endType(x=136, y=180))
        map.add_arc(a)
        an = an + 1

    pn = pn + 1

# write SBGN to file
sbgn.write_file('nl2sbgn.sbgn')
