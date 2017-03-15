#!/usr/bin/env python
"""
**Module**: Hermod
    :platform: Linux
    :synopsis: Listens and handles FSO HTTP API requests
.. moduleauthor:: Richard Ignacio <richard.ignacio@mandiant.com>
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import re

import demjson
from elasticsearch import Elasticsearch
from flask import Flask, request, send_from_directory
from OpenSSL import SSL

__author__ = "Richard Ignacio"
__copyright__ = "Copyright 2007, FireEye Inc."
__version__ = "0.1.2"
__maintainer__ = "Richard Ignacio"
__email__ = "richard.ignacio@mandiant.com"
__status__ = "Development"

# Init flask app
app = Flask(__name__)

# Use SSL or not
USE_SSL = False

# Log file configuration
LOG_FILE = 'hermod.log'

# Elasticsearch configuration
ES_INDEX = 'fsoapi'
ES_TYPE = 'request'
ES_PORT = 9220

IPADDRESS='localhost'
PORT=5050

@app.route('/favicon.ico')
def favicon():
    """Respond to favicon requests by sending the FireEye icon"""
    return send_from_directory(os.path.join(app.root_path, '.'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Intercept all URIs and handle both new requests and status requests
    
    Any URI with an ID at the end requests status for that document from ES. 
    e.g. http://host:5000/a/c/d/e/qUdHfI0NQ8K4TZRIjoxhVw
    
    Any URL with a query string is considered a new request and will be stored
    e.g. http://host:5000/g/h?key1=value1&key2=value2&key3=value3
    """

    id = None
    doc = {}
    response = ''

    # Look for Id
    s = re.search('/([a-zA-Z\-0-9_\.]+)$', request.path)

    if s and not request.args:
        id = s.group(1)
        app.logger.info("Found id: {}".format(id))

    # Get status of existing request
    if id:
        try:
            app.logger.info("Getting info on id: {}".format(id))
            es_response = es.get(index=ES_INDEX, doc_type=ES_TYPE, id=id)
            response = demjson.encode(es_response)
            app.logger.info("Received response from ES: {}".format(response))
        except Exception as e:
            app.logger.error("Error getting elastic search document: {}".format(e))

    # Create a new document
    else:
        doc[u'uri'] = request.path
        doc[u'request'] = {}



        if request.args:
            app.logger.info("Found query string parameters in request")
            useHTML = False
            for key in request.args:
                value = request.args.get(key)
                if key == 'response_type' and value == 'html':
                    useHTML = True
                doc[u'request'][key] = value

            es_response = {}
            try:
                app.logger.info("Saving document to elasticsearch: {}".format(demjson.encode(doc)))
                es_response = es.index(index=ES_INDEX, doc_type=ES_TYPE, body=demjson.encode(doc))
                app.logger.info("Received response from ES: {}".format(str(es_response)))
            except Exception as e:
                app.logger.error("Error saving elastic search document: {}".format(e))

            if useHTML:
                response = '<html><body><br><br><h3><center>Request Submitted</center></h3>' \
                           '<br><center>(ID# {})</center><br>' \
                           '<br><br><center><A HREF="#" onClick="history.back();return false;">Go back</A>' \
                           '</center></body></html>'.format(es_response['_id'])
            else:
                response = str(demjson.encode(es_response))

    return response


if __name__ == "__main__":

    # Init elasticsearch
    es = Elasticsearch(port=ES_PORT)

    logHandler = RotatingFileHandler('hermod.log', maxBytes=5000, backupCount=2)
    fmt = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] : %(message)s')
    logHandler.setFormatter(fmt)

    # set the log handler level
    logHandler.setLevel(logging.INFO)

    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(logHandler)
    app.logger.info("===== Log start of hermod.py version: {} =====".format(__version__))

if USE_SSL:
    context = SSL.Context(SSL.TLSv1_2_METHOD)
    cer = os.path.join(os.path.dirname(__file__), '../ssl.d/server.crt')
    key = os.path.join(os.path.dirname(__file__), '../ssl.d/server.key')
    context = (cer, key)
    app.run(host=IPADDRESS, port=PORT, debug=True, ssl_context=context)
else:
    app.run(host=IPADDRESS, port=PORT)
