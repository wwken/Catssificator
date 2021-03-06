#!/usr/bin/python
# Copyright (c) 2015 Ken Wu
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
# -----------------------------------------------------------------------------
#
# Author: Ken Wu
# Date: 2014 Dec - 2015


from bs4 import BeautifulSoup

import sys
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname('__file__')), './../../../../../src/main/python/'))

from lib.utils import index_of
from urlparse import urlsplit

exclude_lists=[('(',')'), ('[', ']')]



def get_base_url(url):
	base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
	return base_url

def get_path_url(url):
	return urlsplit(url).path

def get_leaf(url):
	if '/' in url:
		return url[url.rindex('/')+1:]
	else:
		return url

def local_path_append(p1, p2):
	if p1[-1:] == '/':
		p1=p1[0:len(p1)-1]
	return p1+p2

def get_text_from_xpath_element(xpath_ele):
	parsed_html = BeautifulSoup(xpath_ele.extract())
	return _filter_out_pattern(parsed_html.get_text(), exclude_lists)


#File IO part


#s is an input string
#exclude_lists is a list of pairs of symbol, like [('(', ')'), ('[', ']') ...etc ]
def _filter_out_pattern(s, exclude_lists):
	for e in exclude_lists:
		while(True):
			start=index_of(s, e[0])
			end=index_of(s, e[1], start) if start else None
			if start and end:
				s = s[:start].rstrip() + ' ' + s[end+1:].lstrip()
			else:
				break
	return s

