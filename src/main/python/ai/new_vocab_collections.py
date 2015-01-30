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

from lib.singleton import Singleton
from backend.nosql_database import AI_NoSqlDatabase

@Singleton
class NewVocabCollections(object):
	
	_db = None
	
	def __init__(self):
		self._db = AI_NoSqlDatabase.Instance()

	def add(self, w):
		try:
			is_m = self.is_member(w)
		except IndexNotFoundException as e:
			is_m = False
		doc = dict(new_vocab=w)
		self._db.add_to_new_vocab(doc)
		
	def is_member(self, w):
		r = self._db.get_from_new_vocab(w)
		if r:
			return True
		else:
			return None
