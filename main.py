import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from collections import defaultdict


tag_map = defaultdict(lambda: wn.NOUN)
tag_map['J'] = wn.ADJ
tag_map['V'] = wn.VERB
tag_map['R'] = wn.ADV

lemma_list = []

text = "RAF and ATP produce RAF and ADP. RAS regulates this process."
tokens = word_tokenize(text)
lemma_function = WordNetLemmatizer()
for token, tag in pos_tag(tokens):
    lemma = lemma_function.lemmatize(token, pos=tag_map[tag[0]])
    lemma_list.append(lemma)
    print(token, "=>", lemma)

print(lemma_list)
grammar = "NP: {<NN>?<VB>*<NN>}"
cp = nltk.RegexpParser(grammar)
result = cp.parse(pos_tag(tokens))
#print(result)


#### render SBGN diagram

import libsbgnpy.libsbgn as libsbgn
from libsbgnpy.libsbgnTypes import Language, GlyphClass, ArcClass, Orientation

# create empty sbgn
sbgn = libsbgn.sbgn()

# create map, set language and set in sbgn
map = libsbgn.map()
map.set_language(Language.PD)
sbgn.set_map(map)

# create a bounding box for the map
box = libsbgn.bbox(x=0, y=0, w=363, h=253)
map.set_bbox(box)

# create some glyphs
g = libsbgn.glyph(class_=GlyphClass.ENTITY, id='glyph1')
g.set_label(libsbgn.label(text='Ethanol'))
g.set_bbox(libsbgn.bbox(x=40, y=120, w=60, h=60))
map.add_glyph(g)

# arcs
# create arcs and set the start and end points
a = libsbgn.arc(class_=ArcClass.CONSUMPTION, source="glyph1", target="pn1.1", id="a01")
a.set_start(libsbgn.startType(x=98, y=160))
a.set_end(libsbgn.endType(x=136, y=180))
map.add_arc(a)