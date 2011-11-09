# Copyright 2011 Red Hat Inc.
# Author: Kushal Das <kdas@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.
import os
import cgi
import sys
from dark_api import *
import json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class customHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path, values = parsepath(self.path)
        if path in ['/','/index.html','/index.html/']:
            self.serve_index()
        elif path == '/style.css':
            self.serve_css()
        elif path == '/serverversion':
            self.serve_version()
        elif path == '/buildids':
            self.serve_api('buildids', values)
        else:
            self.serve_index()
        return

    def serve_api(self, name, values):
        """
        Serve a particular API
        """
        if name == 'buildids':
            data = find_buildids(values)
        
        self.send_response(200)                
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(data)
        
    def serve_version(self):
        """
        Serve the API version
        """
        data = json.dumps({'server-version':'0.1'})
        self.send_response(200)                
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(data)
                
           
                
    def serve_index(self):
        """
        Serve the index API page
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(open('static/index.html').read())
            
    def serve_css(self):
        """
        Serve style.css 
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
        self.wfile.write(open('static/style.css').read())
    
    def do_POST(self):
        global rootnode
        ctype,pdict = cgi.parse_header(self.headers.getheader('Content-type'))
        print ctype , pdict
        if ctype == 'multipart/form-data':
                query = cgi.parse_multipart(self.rfile, pdict)
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Post!')

def main():
    try:
        if len(sys.argv) >= 2:
            port = int(sys.argv[1])
        else:
            port = 8080
        server = HTTPServer(('',port),customHTTPServer)
        print 'server started at port %s' % port
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__=='__main__':
        main()
