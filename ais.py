from flask import Flask, make_response

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/_/health')
def health():
    return make_response('', 200)


def main():
    app.run()


if __name__ == '__main__':
    main()
