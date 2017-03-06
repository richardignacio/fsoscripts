import demjson
from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Configuration
LOG_FILE = 'hermod.log'

@app.route("/")
def root():
    return ""


@app.route("/api/")
def api():
    return ""


@app.route("/api/action/analyze/", methods=['GET','POST'])
def analyze():
    """Accept requests for executing forensics tools then post requests to elasticsearch

        This endpoint accepts either GET or POST.

        The following are the allowable parameters in the query string (GET) or keys in the JSON object (POST):
            - host : Name or IP of host that contains the tool and artifacts
            - username : SSH username to access host
            - password : Password for username
            - tool : Must be "volatility" or "log2timeline"
            - profile: Platform to base analysis on (e.g. winxp)
            - module : Volatility module to use (N/A to log2timeline)
            - artifact_full_path : Full path on host, including file name to memory image (volatility) or
                                   artifacts directory (log2timeline)
            - output_full_path : Full path, including file name, to save output

        Returns a 202 (Accepted) HTTP response code if successful

        Example requests:

        GET:
        http://127.0.0.1:5000/api/action/analyze/?host=sift.test.com&artifact_full_path=/cases/win7.vmsn&
        username=alice&password=Eve123-$&output_full_path=/cases/timeliner.txt&tool=volatility&
        module=timeliner&profile=Win7SP1x64

        POST:
        http://127.0.0.1:5000/api/action/analyze/
        (Body)
        {
            "host" : "sift.test.com",
            "username" : "alice",
            "password" : "Eve123-$",
            "tool" : "volatility",
            "module" : "timeliner",
            "artifact_full_path" : "/cases/win7.vmsn",
            "output_full_path" : "/cases/timeliner.txt"
        }
    """

    response = ""
    code = None

    if request.method == 'GET':
        command = ""
        if request.args.get("tool") == "volatility":
            command = "/usr/bin/vol.py -f {} {} --profile={} --output-file={}".format(
                request.args.get("artifact_full_path"),
                request.args.get("module"),
                request.args.get("profile"),
                request.args.get("output_full_path"))

        if request.args.get("tool") == "log2timeline":
            command = "/usr/bin/log2timeline -z local -f {} -r -p {} > {}".format(
                request.args.get("profile"),
                request.args.get("artifact_full_path"),
                request.args.get("output_full_path")
            )

        document = {
            'endpoint' : '/api/action/analyze/',
            'request' : {
                'host' : str(request.args.get("host")),
                'username' : str(request.args.get("username")),
                'password' : str(request.args.get("password")),
                'tool' : str(request.args.get("tool")),
                'module' : str(request.args.get("module")),
                'profile': str(request.args.get("profile")),
                'artifact_full_path' : str(request.args.get("artifact_full_path")),
                'output_full_path' : str(request.args.get("output_full_path")),
                'command' : str(command)
            },
            'status' : 'requested'
        }

        es_document = demjson.encode(document)
        app.logger.info('GET /api/action/analyze/ Crafted JSON: {}'.format(es_document))
        response = demjson.encode({ 'status' : 'requested' })
        code = 202

    if request.method == "POST":
        received = request.get_json()

        if received['tool'] == 'volatility':
            output = "volatility"

        response = "<pre>" + output + "</pre>"
        code = 202

    return response, code

if __name__ == "__main__":

    # For access.log
    # logger = logging.getLogger('werkzeug')
    # handler = logging.FileHandler('access.log')
    # logger.addHandler(handler)
    # initialize the hermod log handler

    logHandler = RotatingFileHandler('hermod.log', maxBytes=10000, backupCount=1)
    fmt = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] : %(message)s')
    logHandler.setFormatter(fmt)

    # set the log handler level
    logHandler.setLevel(logging.INFO)

    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(logHandler)
app.run()
