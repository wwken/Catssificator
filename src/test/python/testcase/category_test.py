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
from backend.category import Category
from lib.config import Config
from lib.utils import debug
from backend.database import SQLDatabase
import unittest

class CategoryTest(unittest.TestCase):

	_category = None
	_test_dir=join(abspath(dirname('__file__')), '../../../config/test/')
	
	def setUp(self):
		#config_file = self._test_dir + 'setup-test.yaml'
		#Config.Instance().set_config_path(config_file)
		Config.Instance().set_mode('prod')
		
		self._category=Category.Instance()
		#cat_file = self._test_dir +'test-category-production.txt'
		#self._category.set_path(cat_file)
			

	def test_category_prod_mode_get_single_category(self):
		category_str = self._category.get_name(3456, full_path=True)
		self.assertEqual(category_str, 'Health & Beauty > Personal Care > Shaving & Grooming > Hair Clippers & Trimmers')
		
		category_str = self._category.get_name(5555, full_path=True)
		self.assertEqual(category_str, 'Sporting Goods > Team Sports > Softball')
		
		#also make sure the category gets save to the database
		#debug() 
		#returned_category_num = SQLDatabase.Instance().select_category(category='Softball')[0][0]
		#self.assertEqual(returned_category_num, 5555)
		
	
	def test_category_prod_mode_get_all_categories(self):
		cats = self._category.get_categories()
		self.assertEqual(cats[0][1], 'Animals & Pet Supplies')
		self.assertEqual(cats[1][1], 'Apparel & Accessories')
		self.assertEqual(cats[2][1], 'Arts & Entertainment')
		
	def test_category_prod_mode_get_specific_category(self):
		#
		cats = self._category.get_categories_by_name("Arts & Entertainment")
		self.assertEqual(cats[0][1], 'Hobbies & Creative Arts')
		self.assertEqual(cats[1][1], 'Party & Celebration')
		self.assertEqual(len(cats), 2)
		
		cats = self._category.get_categories_by_name("NON EXISTS - BULLSHIT")
		self.assertEqual(cats, None)
		#self.assertEqual(cats[2][1], 'Arts & Entertainment')
	
	def test_category_prod_mode_get_full_name(self):
		cat = self._category.get_full_name('Live%20Animals')
		self.assertEqual(cat, 'Animals & Pet Supplies > Live Animals')

	def test_category_suggestions(self):
		#suggestions = self._category.suggest_categories("sleepwear and lo")
		#self.assertEquals(len(suggestions['suggestions']), 5)	#make sure it returns as exactly 5 categories
		#suggestions = self._category.suggest_categories("lo sleepwear")
		#self.assertEquals(len(suggestions['suggestions']), 5)	#make sure it returns as exactly 5 categories
		#suggestions = self._category.suggest_categories("lo and sleep")
		#self.assertEquals(len(suggestions['suggestions']), 5)	#make sure it returns as exactly 5 categories
		
		#debug()
		suggestions = self._category.suggest_categories("Suits",limit=10, sub_category=False)
		self.assertEquals(len(suggestions['suggestions']), 1)
		
		suggestions = self._category.suggest_categories("mobile p")
		self.assertEqual(len(suggestions['suggestions']), 0)	#make sure it returns more than 5 results
		
		suggestions = self._category.suggest_categories("fuxk TOYS")
		self.assertEqual(len(suggestions['suggestions']), 0)	#make sure it returns nothing
		
	def test_category_suggestion_accuracy(self):
		#debug()
		suggestions = self._category.suggest_categories("mobile phone", sub_category=False)
		self.assertEqual(len(suggestions['suggestions']), 1)    #make sure it just matches on category
		
		suggestions = self._category.suggest_categories("Mobile Phones", sub_category=False)
		self.assertEqual(len(suggestions['suggestions']), 1)    #make sure it just matches on category
		
		#This tests for the hypernyms: A is B if A's hypernyms is B
		#debug()
		suggestions = self._category.suggest_categories("midsize car", sub_category=False) #This should get map to midsize vehicle
		self.assertEqual(len(suggestions['suggestions']), 1)    #make sure it just matches on category
		
		#debug()
		suggestions = self._category.suggest_categories("luxury vehicle", sub_category=False) #This should get map to midsize vehicle
		self.assertEqual(len(suggestions['suggestions']), 1)    #make sure it just matches on category
		self.assertEqual(suggestions['suggestions'][0]['value'], 'Luxury_Cars')
		self.assertLessEqual(suggestions['suggestions'][0]['score'], 0.8)
		
		#suggestions = self._category.suggest_categories("luxury vehicle", sub_category=False)
		#self.assertEqual(len(suggestions['suggestions']), 1)    #make sure it just matches on category
	
	def tearDown(self):
		pass
		#Config.Instance().set_mode('dev')
		#cat_file = self._test_dir +'test-category.txt'
		#self._category.set_path(cat_file)