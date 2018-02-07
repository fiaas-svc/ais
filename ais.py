from flask import Flask, request, make_response
import json
import boto3

app = Flask(__name__)
app.config.from_pyfile('config.cfg')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/<namespace>/<tag>', methods=['POST'])
def tag(namespace, tag):
    data = request.get_json(force=True)
    _write_to_s3(namespace, tag, data)
    return make_response('', 200)


def _write_to_s3(namespace, tag, data):
    s3 = boto3.resource('s3')
    s3object = s3.Object(app.config.get('S3BUCKET'), '%s/%s.json' % (namespace, tag))
    s3object.put(Body=json.dumps(data, indent=4))


@app.route('/_/health')
def health():
    return make_response('', 200)


def main():
    app.run()


if __name__ == '__main__':
    main()
