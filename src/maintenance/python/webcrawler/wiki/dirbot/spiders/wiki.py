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

from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import log

from os.path import abspath, join, dirname
import sys
sys.path.insert(0, join(abspath(dirname('__file__')), './../'))
from common.utils_webcrawler import get_text_from_xpath_element,get_base_url,get_path_url,local_path_append,get_leaf

sys.path.insert(0, join(abspath(dirname('__file__')), './../../../../../src/main/python/'))
from lib.utils import debug,ensure_dir_exists,write_to_local,is_path_exist,convert_s_to_date,get_file_modified_time,add_seconds_to_datetime,get_time_now,generate_md5
from lib.config import Config
from backend.category import Category

import sys
from urlparse import urljoin

''''''''''''''''''''''''''''''''''''''''''''
'''Configuration stuffs starts from here '''
''''''''''''''''''''''''''''''''''''''''''''
LOCAL_DIR = '/tmp/catssificator/webcrawler'
LOCAL_SERVER_DIR = 'http://localhost:8080/' + 'static/webcrawler'
ORIGIN_URL_DIR= 'http://en.wikipedia.org'
NUM_OF_SECONDS_TO_REFRESH_NEW_FILE = 60*60*24*30    #which gives a month of expiration 

INTERNAL_DELIMILER='--->'
UPPER_EXTRACT_LIMIT = 3

''''''''''''''''''''''''''''''''''''''''''''
'''Configuration stuffs ends here '''
''''''''''''''''''''''''''''''''''''''''''''

ensure_dir_exists(LOCAL_DIR, create_multiple=True)

Config.Instance().set_mode('prod')
cat_dir=join(abspath(dirname('__file__')), '../../../../../config/')
cat_file = cat_dir +'category-production.txt'
Category.Instance().set_path(cat_file)

class WikiSpider(Spider):
    name = "wiki"
    allowed_domains = ["wikipedia.org"]
    start_urls = [
        "http://en.wikipedia.org/wiki/IPhone"
        #"http://en.wikipedia.org/wiki/Mid-size"
        #LOCAL_SERVER_DIR+'/wiki/IPhone'
    ]
    _processed_url_dict={}
    _item_dicts={}

    def parse(self, response):
        sel = Selector(response)
        this_subject=sel.xpath('//h1[@id="firstHeading"]/text()')[0]._root
        sites = sel.xpath('//div[@id="mw-content-text"]/p')
        items = []
        this_url=response._url
        cur_body = response.request._body
        for site in sites[:UPPER_EXTRACT_LIMIT]:
            
            '''First see if this page is in any cateory
            '''
            leaf_token=this_subject
            #sug_catgories = Category.Instance().suggest_categories(leaf_token, sub_category=False)
            #if sug_catgories['suggestions']:
            #    ii=0
            
            if len(self._item_dicts) % 50 == 0 and len(self._item_dicts) > 49:
                debug()
                log.msg('content of the dictionary:: %s' %(self.get('iPhone')))
            
            item_names = site.xpath('a/text()').extract()
            #log.msg('Now processing: %s' %(leaf_token))
            self.insert_item_names(leaf_token, item_names)
            
            item_urls = site.xpath('a/@href').extract()
            parsed_text = get_text_from_xpath_element(site)
            this_url=response._url
            base_url=get_base_url(response._url)
            local_path=local_path_append(LOCAL_DIR, get_path_url(response._url))
            write_to_local(local_path, response._body, refresh_seconds=NUM_OF_SECONDS_TO_REFRESH_NEW_FILE)
            
            this_body = cur_body+INTERNAL_DELIMILER+leaf_token
            for item_url in item_urls:
                if not self.add_to_dict(item_url):
                    log.msg('EXists - %s!!!' % (item_url),level=log.DEBUG)
                    continue
                #write to local disk first
                item_full_url=urljoin(base_url, item_url)
                #local_path=local_path_append(LOCAL_DIR, get_path_url(item_full_url))
                #should_use_local_file = self.is_use_local_file(local_path)
                u_r_l = item_full_url
                #if should_use_local_file:
                #    u_r_l = LOCAL_SERVER_DIR + item_url
                
                yield Request(u_r_l,
                    callback=self.parse,
                    errback=self.handle_error,
                    body=this_body
                    )
            #item['description'] = '???'
        
        #return
        #return items
    
    def get(self, name):
        if name in self._item_dicts:
            return self._item_dicts[name]
        else:
            return ''
    
    def add_to_dict(self, u):
        if not self._exist_in_dict(u):
            self._processed_url_dict[u] = 1
            return True
        else:
            return False
    
    #This method add a list of item_names in to the dictionary
    def insert_item_names (self, leaf_token, item_names):
        if not item_names:
            return
        if leaf_token not in self._item_dicts:
            self._item_dicts[leaf_token] = []
        h = generate_md5(item_names)
        #make sure i did not store it before
        for k in self._item_dicts[leaf_token]:
            t_h = k[0]
            if h == t_h:
                log.msg('This row has been inserted before - %s !!!' % (item_names),level=log.DEBUG)
                return
        content = (h, set(item_names))
        self._item_dicts[leaf_token].append(content)
    
    def _exist_in_dict(self, u):
        return u in self._processed_url_dict
        
    def handle_error(self, response):
        print str(response)
    
    def is_use_local_file(self, local_path, refresh_seconds=NUM_OF_SECONDS_TO_REFRESH_NEW_FILE):
        if is_path_exist(local_path):
            if refresh_seconds>0:
                modified_dt=convert_s_to_date(get_file_modified_time(local_path), format="%a %b %d %H:%M:%S %Y")
                modified_dt_plus_refresh = add_seconds_to_datetime(modified_dt, refresh_seconds)
                now=get_time_now()
                if now > modified_dt_plus_refresh:
                    del_file(local_path)
        return is_path_exist(local_path)
    
    def closed(self, reason):
        log(self._processed_url_dict, level=log.INFO)
        #log(len(self._processed_url_dict), level=log.INFO)
