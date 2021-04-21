import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from collections import defaultdict

tag_map = defaultdict(lambda: wn.NOUN)
tag_map['J'] = wn.ADJ
tag_map['V'] = wn.VERB
tag_map['R'] = wn.ADV

text = "RAF and ATP produce RAF and ADP. RAS regulates this process."
tokens = word_tokenize(text)
lemma_function = WordNetLemmatizer()
for token, tag in pos_tag(tokens):
    lemma = lemma_function.lemmatize(token, pos=tag_map[tag[0]])
    print(token, "=>", lemma)

grammar = "NP: {<NN>?<VB>*<NN>}"
cp = nltk.RegexpParser(grammar)
result = cp.parse(pos_tag(tokens))
#print(result)
