#!/usr/bin/python
# Copyright (c) 2014 Ken Wu
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
import sys
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname('__file__')), '../../../src/main/python/'))
from lib.config import Config
from backend.category import Category
from lib.utils import *
import unittest

class UtilsTest(unittest.TestCase):

	_category = None
	_test_dir=join(abspath(dirname('__file__')), '../../../config/test/')
	
	def setUp(self):
		#config_file = self._test_dir + 'setup-test.yaml'
		#Config.Instance().set_config_path(config_file)
		Config.Instance().set_mode('prod')
		
		#cat_file = self._test_dir +'test-category-production.txt'
		#self._category.set_path(cat_file)

	def test_cross_product(self):
		m=[[1,2,3],['a','b'],['r','q','s']]
		r = cross_product_on_all_lists(m)
		self.assertEqual(r, [[1, 'a', 'r'], [1, 'a', 'q'], [1, 'a', 's'], [1, 'b', 'r'], [1, 'b', 'q'], [1, 'b', 's'], [2, 'a', 'r'], [2, 'a', 'q'], [2, 'a', 's'], [2, 'b', 'r'], [2, 'b', 'q'], [2, 'b', 's'], [3, 'a', 'r'], [3, 'a', 'q'], [3, 'a', 's'], [3, 'b', 'r'], [3, 'b', 'q'], [3, 'b', 's']])	
		
		m=[None,['a','b', 'c']]
		r = cross_product_on_all_lists(m)
		self.assertEqual(r, [['a', 'b', 'c']])
		
		m=[['a','b', 'c'], None]
		r = cross_product_on_all_lists(m)
		self.assertEqual(r, [['a', 'b', 'c']])	
		
		#also make sure the category gets save to the database
		#debug() 
		#returned_category_num = SQLDatabase.Instance().select_category(category='Softball')[0][0]
		#self.assertEqual(returned_category_num, 5555)
		
	
	def test_wiki_words_sum_stats(self):
		p = 'data/webcrawler/wiki/Erin_Burnett'
		debug()
		raw_html = read_lines(p, as_single_line=True)
		f=wiki_extract_html_contents
		extracted_html=words_sum_stats(raw_html, f)
		print extracted_html
		
	def tearDown(self):
		pass
		#Config.Instance().set_mode('dev')
		#cat_file = self._test_dir +'test-category.txt'
		#self._category.set_path(cat_file)