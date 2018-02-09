from flask import Flask, request, make_response, abort
import json
import boto3
from datetime import datetime
import os

app = Flask(__name__)


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
    s3object = s3.Object(os.environ['S3BUCKET'], '%s/%s.json' % (channel, tag))
    s3object.put(Body=json.dumps(data, indent=4))


def _verify(data):
    for k in ['updated', 'image', 'build', 'commit']:
        if k not in data:
            abort(400, '%s must be specified' % k)


@app.route('/_/health')
def health():
    return make_response('', 200)


def main():
    app.run()


if __name__ == '__main__':
    main()
