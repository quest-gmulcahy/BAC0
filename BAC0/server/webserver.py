#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under LGPLv3, see file LICENSE in this source tree.
"""
This will start a flask server and bokeh serve will be integrated to
the flask app.

This code comes from Adam

"""
#imports to run a bokeh server in code, as opposed to running 'bokeh serve *args*' as a command line argument
from bokeh.server.server import Server
from bokeh.command.util import build_single_handler_applications
from bokeh.application import Application

#imports to run my server
from bokeh.embed import autoload_server #to put bokeh in the flask app
from flask import Flask,render_template, redirect, url_for, request,session
import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.autoreload
import sys
from collections import OrderedDict
import threading
import time


class BAC0WebServer(object):
    #setup flask 
    flaskApp = Flask(__name__)
    flaskApp.debug = True
    
    def __init__(self):
        #initialize some values, sanatize the paths to the bokeh plots
        self.argvs = {}
        self.urls = ['trends']
        self.host = 'localhost'
        self.app_port = 5567
        self.bokeh_port = 6060
    
    def run_bokeh_server(self, bok_io_loop):
            ##turn file paths into bokeh apps
            self.app = Application()
            ##args lifted from bokeh serve call to Server, with the addition of my own io_loop
            kwags = {
                'io_loop':bok_io_loop,
                'generade_session_ids':True,
                'redirect_root':True,
                'use_x_headers':False,
                'secret_key':None,
                'num_procs':1,
                'host':['%s:%d'%(self.host,self.app_port),'%s:%d'%(self.host,self.bokeh_port)],
                'sign_sessions':False,
                'develop':False,
                'port':self.bokeh_port,
                'use_index':True
            }
            self.srv = Server(self.app,**kwags)
        
        
    @flaskApp.route('/',methods=['GET']) #a sample page to display the bokeh docs
    def graph_page(self):
        print('graph_page')
        #pull the bokeh server apps
        bokeh_scripts = {} 
        for plot in self.urls:
            bokeh_scripts[plot]=autoload_server(model=None, url='http://%s:%d'%(self.host,self.bokeh_port), app_path="/"+plot) # pulls the bokeh apps off of the bokeh server
        
        #order the plots
        all_divs= OrderedDict()
        all_divs.update(bokeh_scripts)
        all_divs = OrderedDict(sorted(all_divs.items(), key=lambda x: x[0]))
        
        #throw the plots on a jinja2 template
        return render_template('templates/graph_template.html',div_dict=all_divs)
    
    
    def rest_of_tornado(self, io_loop_here):
        ##a test to see if I can shutdown while the server is running. This will eventually get a button somewhere.
        print('starting countdown')
        time.sleep(10)
        print('countdown finished')    
        io_loop_here.stop()
    
    
    def start_the_thing(self):
        #initialize the tornado server
        http_server = tornado.httpserver.HTTPServer(
                tornado.wsgi.WSGIContainer(self.flaskApp)
            )
        http_server.listen(self.app_port)
        io_loop = tornado.ioloop.IOLoop.instance()
        tornado.autoreload.start(io_loop)
        
        #call the turn off test
        #nadostop = threading.Thread(target=self.rest_of_tornado,args=(io_loop,))
        #nadostop.start()
        
        #add the io_loop to the bokeh server
        self.run_bokeh_server(io_loop)
        print('starting the server on http://%s:%d/'%(self.host,self.app_port))
        
        #run the bokeh server
        io_loop.start()