import json
from flask import Flask, request, send_file, Response
from flask_cors import CORS
import psycopg2
import pandas as pd
import os
from parsers import parse_investor_details

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})

if ".env" in os.listdir():
    from dotenv import load_dotenv
    load_dotenv()

POSTGRES_URL = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB =  os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PW = os.environ.get("POSTGRES_PASSWORD")

global conn, cur
conn = psycopg2.connect(host=POSTGRES_URL, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PW)
cur = conn.cursor()


@app.route("/get_investor_details", methods=["POST"])
def get_investor_details():
    global conn, cur
    results = []
    data = request.get_json()
    print(data, "get_investor_details")

    try:
        investor_name = data["investor_name"].lower()
    except Exception as e:
        return Response(response=json.dumps({"results": "Malformed JSON"}), status=300)
    
    query = 'SELECT (investor_name, cik) FROM all_investors WHERE investor_name ~ %s'

    try:
        cur.execute(query, (f".*{investor_name}.*",))
        results = cur.fetchall()
    except Exception as e:
        print(e)
        conn = psycopg2.connect(host=POSTGRES_URL, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PW)
        cur = conn.cursor()
        return Response(response=json.dumps({"results": "DATABASE ERROR CHECK QUERY"}), status=300)
    
    if len(results) == 0:
        return Response(response=json.dumps({"results": "CIK NOT FOUND"}), status=300)
    
    results = pd.DataFrame([parse_investor_details(result[0]) for result in results])
    results.columns = ["investor_name", "cik"]
    payload = {
            "investor_name": results["investor_name"].to_list(),
            "cik": results["cik"].to_list()
    }

    return Response(response=json.dumps({"results": payload}), status=200)

@app.route("/get_issuer_details", methods=["POST"])
def get_issuer_details():
    global conn, cur
    results = []
    data = request.get_json()
    print(data, "get_issuer_details")

    try:   
        issuer_name = data["issuer_name"].lower()
    except Exception as e:
        return Response(response=json.dumps({"results": "Malformed JSON"}), status=300)

    query = "SELECT (name_of_issuer, cusip) FROM asset_cusip_lookup WHERE name_of_issuer ~ %s"
    
    try:
        cur.execute(query, (f".*{issuer_name}.*",))
        results = cur.fetchall()
    except Exception as e:
        print(e)
        conn = psycopg2.connect(host=POSTGRES_URL, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PW)
        cur = conn.cursor()
        return Response(response=json.dumps({"results": "DATABASE ERROR CHECK QUERY"}), status=300)

    if len(results) == 0:
        return Response(response=json.dumps({"results": "CUSIP NOT FOUND"}), status=300)
    
    results = pd.DataFrame([parse_investor_details(result[0]) for result in results])
    results.columns = ["investor_name", "cusip"]
    results["issuer_code"] = results["cusip"].apply(lambda x: x[:6])
    payload = {
            "name_of_issuer": results["investor_name"].to_list(),
            "cusip": results["cusip"].to_list(),
            "issuer_code": results["issuer_code"].to_list()
    }
    return Response(response=json.dumps({"results": payload}), status=200) # SHOWING THE FIRST RESULT ONLY

@app.route("/get_filings", methods=["POST"])
def get_filings():
    global conn, cur
    results = []
    data = request.get_json()
    print(data, "get_filings")

    try:   
        db_query = data["db_query"]
    except Exception as e:
        return Response(response=json.dumps({"results": "Malformed JSON"}), status=300)
    
    try:
        cur.execute(db_query)
        results = cur.fetchall()
    except Exception as e:
        print(e)
        conn = psycopg2.connect(host=POSTGRES_URL, port=POSTGRES_PORT, database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PW)
        cur = conn.cursor()
        return Response(response=json.dumps({"results": f"DATABASE ERROR {e}"}), status=300)
    
    if len(results) == 0:
        return Response(response=json.dumps({"results": "NO RESULTS FOUND"}), status=300)
    
    csv_string = pd.DataFrame(results).to_csv(index=False)
    return Response(response=json.dumps({"results": csv_string}), status=200)


# no changes below
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
