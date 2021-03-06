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
from utils import *

class Loggable(object):
    
    @property
    def run_time_name(cls):
        return cls.__class__.__name__
        
    def getLogger(self):
        return get_logger(self.run_time_name)
    
    def info(self, message):
        self.getLogger().info(message)
    
    def warn(self, message):
        self.getLogger().warn(message)
    
    def debug(self, message):
        self.getLogger().debug(message)

    def error(self, message):
        self.getLogger().error(message)