import json
from flask import Flask, request, send_file, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})

@app.route("/get_investor_cik", methods=["POST"])
def get_investor_cik():
    data = request.get_json()
    print(data, "get_investor_cik")
    return Response(response=json.dumps({"results": "12345"}), status=200)

@app.route("/get_issuer_cusip", methods=["POST"])
def get_issuer_cusip():
    data = request.get_json()
    print(data, "get_issuer_cusip")
    return Response(response=json.dumps({"results": "54321"}), status=200)

@app.route("/get_filings", methods=["POST"])
def get_filings():
    data = request.get_json()
    print(data, "get_filings")
    return Response(response=json.dumps({"results": [1, 2, 3, 4, 5]}), status=200)


@app.route("/logo.png", methods=["GET"])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="text/json")

@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0")

if __name__ == "__main__":
    main()
