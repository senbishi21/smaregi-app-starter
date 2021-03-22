### [main]
import firebase_admin, datetime, json, pytz, os, urllib, requests, base64, math, csv, random, subprocess

from flask import Flask, redirect, request, make_response, render_template, send_file
from firebase_admin import firestore, credentials
from subprocess import PIPE
from google.cloud import error_reporting
from google.oauth2 import service_account
from google.cloud import storage

# initiate Cloud Logging Logger
cf_name = os.environ.get('K_SERVICE', 'local')
cf_version = os.environ.get('K_REVISION', 'xxx')

# Settings
Firestore_projectID = os.environ.get('projectID', '')
client_id = os.environ.get('app_client_id', '')
client_secret = os.environ.get('app_client_secret', '')
local_contract_id = os.environ.get('local_contract_id', '')

env = os.environ.get('env', 'local')
if env == "local":
    Auth_end_point = "https://id.smaregi.dev"
    API_end_point = "https://api.smaregi.dev"
    login_redirect_url=""
    session_collection_name = "qa-session-and-tokens"
    cookie_name = "smaregi-app-qa"

elif env == "qa":
    Auth_end_point = "https://id.smaregi.dev"
    API_end_point = "https://api.smaregi.dev"
    login_redirect_url = f"https://id.smaregi.dev/authorize?response_type=code&client_id={client_id}&scope=openid"
    session_collection_name = "qa-session-and-tokens"
    cookie_name = "smaregi-app-qa"
    client = error_reporting.Client(service=cf_name, version=cf_version)

elif env == "prod":
    Auth_end_point = "https://id.smaregi.jp"
    API_end_point = "https://api.smaregi.jp"
    login_redirect_url = f"https://id.smaregi.jp/authorize?response_type=code&client_id={client_id}&scope=openid"
    session_collection_name = "prod-session-and-tokens"
    cookie_name = "smaregi-app-prod"
    client = error_reporting.Client(service=cf_name, version=cf_version)

def entrypoint(request):

    cookie = request.cookies.get(cookie_name, None)
    contract_id = validate_cookie_and_get_contractID(cookie)
    
    # If no session cookie or expired, go redirect to Open ID Connect (OIDC)
    if contract_id is None:
        return redirect_to_OIDC()
    else:
        return main_page(contract_id)


########## start GET method func ##########
def redirect_to_OIDC():
    return redirect(login_redirect_url, code=302)

def main_page(contract_id):

    return f"Hello World! Your contract ID is {contract_id}"


######### start Utility #########
def validate_cookie_and_get_contractID(cookie):
    print("validating cookie:{}".format(cookie))

    if env == "local":
        print(f"!!! valid any cookie for LOCAL testing, using {local_contract_id}")
        return local_contract_id

    if cookie is None:
        print("no session cookie")
        return None

    db = get_firestore_instance()
    doc_ref = db.collection(session_collection_name).document(cookie)
    doc = doc_ref.get()

    # if cookie entry exist in Firestore and within expire date, then go to the main page
    if doc.exists and doc.to_dict()["expires"] > datetime.datetime.now(pytz.timezone('Asia/Tokyo')):
        return doc.to_dict()["contract_id"]
    else:
        print('No such document or cookie expired')
        return None

def get_firestore_instance():
    # init Firebase client if no driver
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': Firestore_projectID,
        })
    db = firestore.client()
    return db


######## start LOCAL TESTING ########
app  = Flask(__name__)
@app.route('/', methods=["GET", "POST"])
def test_entrypoint():
    return entrypoint(request)

if __name__ == '__main__':

    # Initiate Error logger for local
    # For local testing, GCP credential needed
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    error_reporting_credentials = service_account.Credentials.from_service_account_file(cred_path)
    client = error_reporting.Client(project=Firestore_projectID, credentials=error_reporting_credentials, service=cf_name, version=cf_version)

    app.run(host='0.0.0.0',port=8080)

######## end LOCAL TESTING ########
