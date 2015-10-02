#!/usr/bin/python
import libxml2

doc = libxml2.parseFile('data/Erin_Burnett')
for url in doc.xpathEval('//@Url'):
	print url.content
#print xpath.find('//div[@id="mw-content-text"]/p', )