#!/usr/bin/python

from nltk.corpus import wordnet as wn

def syn_set(s):
    ss = wn.synsets(s) 
    return ss if ss else None

def get_hyper(s):  
    ss = syn_set(s)
    hyper = lambda s: s.hypernyms()  
    return map(lambda x: x._lemma_names[0], list(ss[0].closure(hyper))) if ss else None    #just take the first synset as this is the most meaningful
def get_hypo(s):
    ss = syn_set(s)
    hypo = lambda s: s.hyponyms()
    return map(lambda x: x._lemma_names[0], list(ss[0].closure(hypo))) if ss else None    #just take the first synset as this is the most meaningful

w='vehicl'
print 'word: ' + w
print 'hyper: ' + str(get_hyper(w))
print 'hypo: ' + str(get_hypo(w))