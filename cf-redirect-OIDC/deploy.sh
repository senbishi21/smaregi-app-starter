#!/bin/bash
# ./deploy.sh

# 設定ファイル読み込み
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/../_init/credentials"
. $CRED_DIR/secrets.txt
echo "PROJECT ID is ${PROJECT_ID}"

gcloud functions deploy qa-redirect-OIDC --source $SCRIPT_DIR/deploy --set-env-vars env=qa,projectID=${PROJECT_ID},app_client_id=${QA_APP_CLIENT_ID},app_client_secret=${QA_APP_CLIENT_SECRET},main_url=${QA_MAIN_URL} --entry-point login_redirect --runtime python38 --trigger-http --allow-unauthenticated