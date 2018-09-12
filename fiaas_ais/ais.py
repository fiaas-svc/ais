from flask import Flask, request, make_response, abort
from flask_talisman import Talisman, DENY
import json
import boto3
from datetime import datetime
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Histogram

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


def main():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
