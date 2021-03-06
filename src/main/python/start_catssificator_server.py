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
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import urlparse
import json
import tornado.httpserver
import tornado.ioloop
import tornado.web
import thread
import time
import threading, datetime
from threading import Thread
from query_processor import QueryProcessor
from request_ticket_system import RequestTicketSystem
from lib.utils import *
from web.index_page_handler import HomePageHandler, UploadPageHandler, ReportsPageHandler, AboutPageHandler,ChangesPageHandler
from web.api_handler import APIHandler
from web.fileupload_handler import FileUploadHandler
from web.static_file_handler import StaticFileHandler
from lib.config import Config
from web.uibuilder import UIBuilder

log = get_logger("Main")    
server_addr = ('', 9797)
server_addr_2 = ('', Config.Instance().get_yaml_data(['common', 'ui_server_port'], '80'))

class WebStaticFileHandler(StaticFileHandler):
    
    def get(self, path):
        self.get_internal('../../web', path)
        
class UploadDataStaticFileHandler(StaticFileHandler):
    
    _file_upload_base_dir = Config.Instance().get_yaml_data(['common', 'file_upload_base_dir'], 'catssificator-upload')
    
    def get(self, path):
        self.get_internal('../../../../data/'+self._file_upload_base_dir, path)

class CCRequestHandler(BaseHTTPRequestHandler):
  _log = get_logger("CCRequestHandler")
  def do_POST(self):
    form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
    self.send_response(200, "")
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    response_str=''
    ticket_token=''
    category=''
    _from_who=str(self.client_address[0])+':'+str(self.client_address[1])
    for field in form.keys():
      field_item = form[field]
      if field == 'ticket-token':
          ticket_token=form[field].value
      elif field == 'category':
          category=form[field].value
      else:  
          query = form[field].value
          #self._log.info("response_str: %s" % response_str)
    if ticket_token and category: #If it is a request ticket submission mode
        response_str = RequestTicketSystem.Instance().submit(ticket_token, category)
    elif query and category:
        response_str = QueryProcessor().submit(query, category,from_who=_from_who)
    elif query:
        response_str = dumps(QueryProcessor().inquire(query, return_full_categories_if_not_found=True))
    else:
        response_str = '{"result":"no", "message"="invalid request"}'
    self.wfile.write(response_str)
#log.info("Categories: %s" % (c))
application = tornado.web.Application([
    (r'/static/(.*)', WebStaticFileHandler),
    (r'/data/catssificator-upload/(.*)', UploadDataStaticFileHandler), 
    (r'/fileupload', FileUploadHandler),
    (r'/api/(.*)', APIHandler), 
    (r"/", HomePageHandler),
    (r"/upload.html", UploadPageHandler),
    (r"/reports.html", ReportsPageHandler),
    (r"/about.html", AboutPageHandler),
    (r"/changes.html", ChangesPageHandler)
])


_RESTful_server = HTTPServer(server_addr, CCRequestHandler)
new_retry_port=0
def start_RESTFul_server():
    #This is for the command and restful usage
    _RESTful_server.allow_reuse_address = True
    _RESTful_server.serve_forever()

def start_UI_server():
    #This is for interactive Web UI application
    try:
        application.listen(server_addr_2[1])
        log.info('Catssificator web management console has successfully started at: http://127.0.0.1:%s' % (server_addr_2[1]))
    except Exception as e:
        new_retry_port = 8080
        log.error('Port: %s has been taken...trying new port: %s ' % (server_addr_2[1], new_retry_port))
        application.listen(new_retry_port)
        log.info('Catssificator web management console has successfully started at: http://127.0.0.1:%s' % (new_retry_port))
    tornado.ioloop.IOLoop.instance().start() 
    
if __name__ == '__main__':
  try:
    t1 = thread.start_new_thread( start_RESTFul_server, ())
    if Config.Instance().get_mode() == 'prod':
        t2 = thread.start_new_thread( start_UI_server, ())
    else:
        log.info('Catssificator is running as dev (console) mode only.')
    
    UIBuilder.Instance()    #initialize the UIBuilder
    
    log = get_logger('Main')
    while 1:
        RequestTicketSystem.Instance().clean_up() 
        time.sleep(60*60)   #come back in 1 hour
        
  except KeyboardInterrupt:
    print '^C received, shutting down the web servers'
    _RESTful_server.socket.close()
    if Config.Instance().get_mode() == 'prod':
        tornado.ioloop.IOLoop.instance().stop()