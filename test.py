# Import necessary packages
import scispacy
import spacy
from spacy import displacy
from nltk.corpus import wordnet

import libsbgnpy.libsbgn as libsbgn
from libsbgnpy.libsbgnTypes import Language, GlyphClass, ArcClass, Orientation

import tempfile

# Load the NLP model
nlp = spacy.load("en_ner_bionlp13cg_md")

text = """
Myeloid derived suppressor cells (MDSC) are immature 
myeloid cells with immunosuppressive activity. 
They accumulate in tumor-bearing mice and humans 
with different types of cancer, including hepatocellular 
carcinoma (HCC).
"""

text1 = """Further, while specific constitutive binding to the peri-kappa B site 
is seen in monocytes, stimulation with phorbol esters induces additional, specific binding.
Understanding the monocyte-specific function of the peri-kappa B factor may ultimately provide 
insight into the different role monocytes and T-cells play in HIV pathogenesis. 
"""

text2 = """Glucose and ATP produce glucose-6P and ADP."""

# Apply NLP model
doc = nlp(text2)

# Examine the entities extracted by the mention detector.
print(list(doc.ents))

displacy.render(doc, style='ent', jupyter=True)
displacy.render(next(doc.sents), style='dep', jupyter=True)

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

    ent_dic[a] = 'glyph'+str(gn)

    g = libsbgn.glyph(class_=sbgn_glyph, id='glyph'+str(gn))
    g.set_label(libsbgn.label(text=a))
    g.set_bbox(libsbgn.bbox(x=40, y=120, w=60, h=60))
    map.add_glyph(g)

    gn = gn + 1

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
    synonyms = []
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

    pn = pn + 1

# write SBGN to file
sbgn.write_file('E:/test.sbgn')

# from libsbgnpy import render
# render.render_sbgn(sbgn,'E:/test.png')