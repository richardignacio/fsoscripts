#!/usr/bin/env python
"""
**Module**: Hermod
    :platform: Linux
    :synopsis: Listens and handles FSO HTTP API requests
.. moduleauthor:: Richard Ignacio <richard.ignacio@mandiant.com>
"""

import logging
from logging.handlers import RotatingFileHandler
import re

import demjson
from elasticsearch import Elasticsearch
from flask import Flask, request

__author__ = "Richard Ignacio"
__copyright__ = "Copyright 2007, FireEye Inc."
__version__ = "0.1.1"
__maintainer__ = "Richard Ignacio"
__email__ = "richard.ignacio@mandiant.com"
__status__ = "Development"

# Init flask app
app = Flask(__name__)

# Log file configuration
LOG_FILE = 'hermod.log'

# Elasticsearch configuration
ES_INDEX = 'fsoapi'
ES_TYPE = 'request'

IPADDRESS='localhost'
PORT='5050'

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

    # Get status of existing request
    if id:
        try:
            es_response = es.get(index=ES_INDEX, doc_type=ES_TYPE, id=id)
        except Exception as e:
            app.logger.error("Error getting elastic search document: {}".format(e))

        response = demjson.encode(es_response)

    # Create a new document
    else:
        doc[u'uri'] = request.path
        doc[u'request'] = {}

        if request.args:
            for key in request.args:
                value = request.args.get(key)
                doc[u'request'][key] = value

        try:
            es_response = es.index(index=ES_INDEX, doc_type=ES_TYPE, body=demjson.encode(doc))
        except Exception as e:
            app.logger.error("Error saving elastic search document: {}".format(e))

        response = str(es_response)

    return response


if __name__ == "__main__":

    # Init elasticsearch
    es = Elasticsearch()

    logHandler = RotatingFileHandler('hermod.log', maxBytes=10000, backupCount=1)
    fmt = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] : %(message)s')
    logHandler.setFormatter(fmt)

    # set the log handler level
    logHandler.setLevel(logging.INFO)

    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(logHandler)
app.run(host=IPADDRESS, port=PORT)