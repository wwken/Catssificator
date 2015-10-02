#!/usr/bin/python
from textblob import TextBlob, Word
import string
import Stemmer
stemmer = Stemmer.Stemmer('english')


wds = "luxury"
print 'steam it: ' + stemmer.stemWord(wds)



