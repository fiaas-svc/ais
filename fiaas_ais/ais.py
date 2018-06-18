from flask import Flask, request, make_response, abort
from flask_talisman import Talisman, DENY
import json
import boto3
from datetime import datetime

app = Flask(__name__)
# TODO: These options are like this because we haven't set up TLS
Talisman(app, frame_options=DENY, force_https=False, strict_transport_security=False)


@app.route('/<channel>/<tag>', methods=['POST'])
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
def health():
    return make_response('', 200)


def main():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
