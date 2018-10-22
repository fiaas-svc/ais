import json
import logging
import sys
from datetime import datetime

from gevent import monkey

# This need to be before boto3
monkey.patch_all()  # NOQA

import boto3
import time

from flask import Flask, request, make_response, abort
from flask_talisman import Talisman, DENY
from gevent.pywsgi import WSGIServer, LoggingLogAdapter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Histogram

LOG = logging.getLogger(__name__)

app = Flask(__name__)
# TODO: These options are like this because we haven't set up TLS
Talisman(app, frame_options=DENY, force_https=False, strict_transport_security=False)

request_histogram = Histogram("web_request_latency", "Request latency in seconds", ["endpoint"])
metrics_histogram = request_histogram.labels("metrics")
tag_release_histogram = request_histogram.labels("release-channel-tag")
health_histogram = request_histogram.labels("health")


@app.route('/<channel>/<tag>', methods=['POST'])
@tag_release_histogram.time()
def tag(channel, tag):
    data = request.get_json(force=True)
    if 'updated' not in data:
        data['updated'] = datetime.now().isoformat()
    _verify(data)
    _write_to_s3(channel, tag, data)
    return make_response('', 200)


def _write_to_s3(channel, tag, data):
    s3 = boto3.resource('s3')
    s3object = s3.Object('fiaas-release.delivery-pro.schibsted.io', '%s/%s.json' % (channel, tag))
    s3object.put(Body=json.dumps(data, indent=4))
    s3object.Acl().put(ACL='public-read')


def _verify(data):
    for k in ['updated', 'image', 'build', 'commit']:
        if k not in data:
            abort(400, '%s must be specified' % k)


@app.route('/_/slow')
def slow():
    time.sleep(1)
    return make_response('', 200)


@app.route('/_/health')
@health_histogram.time()
def health():
    return make_response('', 200)


@app.route("/_/metrics")
@metrics_histogram.time()
def metrics():
    resp = make_response(generate_latest())
    resp.mimetype = CONTENT_TYPE_LATEST
    return resp


def _init_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s|%(levelname)7s] %(message)s [%(name)s|%(threadName)s]"))
    root.addHandler(handler)


def main():
    _init_logging()
    log = LoggingLogAdapter(LOG, logging.DEBUG)
    error_log = LoggingLogAdapter(LOG, logging.ERROR)
    http_server = WSGIServer(("", 5000), app, log=log, error_log=error_log)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
