### [redirect-OIDC]
import requests, urllib, os, firebase_admin, secrets, datetime
from flask import Flask, redirect, request, make_response
from firebase_admin import firestore, credentials
from google.cloud import error_reporting

# initiate Cloud Logging Logger
cf_name = os.environ.get('K_SERVICE', 'local')
cf_version = os.environ.get('K_REVISION', 'xxx')
client = error_reporting.Client(service=cf_name, version=cf_version)

# Settings
Firestore_projectID = os.environ.get('projectID', '')
client_id = os.environ.get('app_client_id', '')
client_secret = os.environ.get('app_client_secret', '')
main_url = os.environ.get('main_url', '')

env = os.environ.get('env', 'local')
if env == "qa":
    Auth_end_point = "https://id.smaregi.dev"
    API_end_point = "https://api.smaregi.dev"
    session_collection_name = "qa-session-and-tokens"
    cookie_name = "smaregi-app-qa"
    session_expire_minutes = 10

elif env == "prod":
    Auth_end_point = "https://id.smaregi.jp"
    API_end_point = "https://api.smaregi.jp"
    session_collection_name = "prod-session-and-tokens"
    cookie_name = "smaregi-app-prod"
    session_expire_minutes = 60

def login_redirect(request):

    # 1. Check OIDC challenge code exist in the request
    if 'code' in request.args:
        auth_code = request.args.get('code')
    else:
        client.report("OIDC rediret request does not have 'code' parameter")
        return "申し訳ございませんが、こちらのURLへの直接のアクセスはご遠慮下さい。"
    
    # 2. Get user access token
    try:
        access_token_list = get_user_access_token(auth_code)
        access_token = access_token_list[0]
        access_token_expires_in = access_token_list[1]
    except Exception as ex:
        client.report(f"Error in get_user_access_token(): {ex}")
        return "申し訳ございませんが、技術的問題が起きているようです。しばらくお待ちいただき、再度アクセスして下さい。"

    # 3. Retrieve contract ID by User Access Token
    try:
        contract_id = get_contract_id(access_token)
        print("contract id is {0}".format(contract_id))
    except Exception as ex:
        client.report(f"Error in get_contract_id(): {ex}")
        return "申し訳ございませんが、技術的問題が起きているようです。しばらくお待ちいただき、再度アクセスして下さい。"

    # 4. Generate random value cookie
    cookie_value = secrets.token_urlsafe(32)
    max_age = 600
    expire_date = datetime.datetime.now() + datetime.timedelta(minutes=session_expire_minutes)

    # 5. Store cookie in Firestore
    try:
        store_cookie_in_Firestore(cookie_value, expire_date, access_token, access_token_expires_in, contract_id)
        print("cookie value:{}".format(cookie_value))
    except Exception as ex:
        client.report(f"Error in store_cookie_in_Firestore(): {ex}")
        return "申し訳ございませんが、技術的問題が起きているようです。しばらくお待ちいただき、再度アクセスして下さい。"

    # 6. back to main page, with setting cookie
    response = make_response(redirect(main_url))
    response.set_cookie(cookie_name, value=cookie_value, expires=expire_date) 
    return response

######## [Shared] Function ########
def get_firestore_instance():
    # init Firebase client if no driver
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {
            'projectId': Firestore_projectID,
        })
    db = firestore.client()
    return db
###################################


# Store generated cookie in Firestore
def store_cookie_in_Firestore(cookie_value, expire_date, access_token, access_token_expires_in, contract_id):

    try:
        db = get_firestore_instance()
        data = {
            u'expires': expire_date,
            u'access_token': access_token,
            u'access_token_expires_in': access_token_expires_in,
            u'contract_id': contract_id
        }

        db.collection(session_collection_name).document(cookie_value).set(data)
    except Exception as ex:
        raise Exception(f"get_firestore_instance() error.\n{ex}\nproject ID:{Firestore_projectID}\nsession_collection_name:{session_collection_name}\ncookie_value:{cookie_value}\nlocal variables:{locals()}")

# Get Smaregi access token based on the auth code
def get_user_access_token(auth_code):

    # get user access token based on the auth code provided from the request
    openID_access_token_url = Auth_end_point + "/authorize/token"
    params = {
        "grant_type":"authorization_code",
        "code":auth_code
    }
    encoded_params = urllib.parse.urlencode(params)

    response = requests.post(openID_access_token_url, data=params, headers={"Content-Type":"application/x-www-form-urlencoded"},auth=(client_id, client_secret))
    if response.status_code != requests.codes.ok:
        raise Exception(f"{openID_access_token_url} API error. HTTP code:{response.status_code}\nreturn value:{response.text}\nauth_code value:{auth_code}\nlocal variables:{locals()}")
    else:
        response_dict = response.json()
        access_token = response_dict['access_token']
        expires_in = response_dict['expires_in']
        return access_token, expires_in

# Get contract ID by user access token
def get_contract_id(access_token):

    openID_get_userinfo = Auth_end_point + "/userinfo"
    headers = {
        "Authorization": "Bearer {0}".format(access_token)
    }
    response = requests.post(openID_get_userinfo, headers=headers)

    if response.status_code != requests.codes.ok:
        raise Exception(f"{openID_get_userinfo} API error. HTTP code:{response.status_code}\nreturn value:{response.text}\naccess_token value:{access_token}\nlocal variables:{locals()}")
    else:
        # email = response['email']
        contract_id = response.json()['contract']['id']
        return contract_id
