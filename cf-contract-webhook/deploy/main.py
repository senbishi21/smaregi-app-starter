### [contract-webhook]
import firebase_admin, datetime, json, pytz, os, urllib, requests, base64

from flask import Flask, redirect, request, make_response, render_template
from firebase_admin import firestore, credentials
from datetime import datetime, timezone, timedelta


env = os.environ.get('env', 'local')
Firestore_projectID = os.environ.get('projectID', '')

if env == "local" or env == "qa":
    Auth_end_point = "https://id.smaregi.dev"
    API_end_point = "https://api.smaregi.dev"
    contract_collection_name="qa-contracts"
elif env == "prod":
    Auth_end_point = "https://id.smaregi.jp"
    API_end_point = "https://api.smaregi.jp"
    contract_collection_name="prod-contracts"

def contract_update_webhook_receiver(request):

    # Get webhook posted data
    request_json = request.get_json()
    action = request_json["action"]
    contract_id = request_json["contractId"]
    plan_dict = request_json["plan"]
    print(f"## webhook raw data: {request_json}")

    # Use current time in JPT at server time. Not using webhook's info:date
    current_time_JP = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    current_time_JP_str = current_time_JP.strftime('%Y-%m-%d')
    MAX_END_TIMESTAMP = datetime(2099, 1, 1, 0, 0, 0, 0000,tzinfo=timezone(timedelta(hours=+9), 'JST'))

    db = get_firestore_instance()
    doc_ref = db.collection(contract_collection_name).document(contract_id)

    if action == "start":
        
        # check existing data
        doc = doc_ref.get()
        if doc.exists:
            print("[WARNING] {0} is return user. Old contract data is {1}".format(contract_id, doc.to_dict()))

        # update Firestore data
        data_to_update = {
            "start_timestamp" : current_time_JP, 
            "last_update_timestamp" : current_time_JP,
            "end_timestamp" : MAX_END_TIMESTAMP,
            "plan" : plan_dict
        }
        doc_ref.set(data_to_update)

        # send PubSub task to sync employee address data immediately
        initial_data_sync(contract_id)


    elif action == "end":

        # check existing data
        doc = doc_ref.get()
        if not doc.exists:
            print("[ERROR] {0} is not a user, but received 'end' webhook message.".format(contract_id))
            return "Error in webhook data"

        # MERGE update Firestore data
        # not include whole data, just update "update_timestamp" and "end_timestamp"
        data_to_update = {
            "last_update_timestamp" : current_time_JP,
            "end_timestamp" : current_time_JP,
            "plan" : plan_dict
        }
        doc_ref.set(data_to_update, merge=True)

    elif action == "change-plan":

        # check existing data
        doc = doc_ref.get()
        if not doc.exists:
            print("[WARNING] {0} is changing plan. Old contract data is {1}".format(contract_id, doc.to_dict()))

        # update Firestore data
        data_to_update = {
            "last_update_timestamp" : current_time_JP,
            "plan" : plan_dict
        }
        doc_ref.set(data_to_update, merge=True)

    else:
        print("[ERROR] unrecognized webhook message. Raw data is: {0}".format(request_json))
        return "error, unrecognized webhook format"

    return "contract ID transaction complete"


def get_firestore_instance():
    # init Firebase client if no driver
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': Firestore_projectID,
        })
    db = firestore.client()
    return db


######## LOCAL TESTING ########
app  = Flask(__name__)

@app.route('/', methods=["POST"])
def test_contract_update_webhook_receiver():
    return contract_update_webhook_receiver(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)

######## LOCAL TESTING ########
