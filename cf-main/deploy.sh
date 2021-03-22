#!/bin/bash
# ./deploy.sh

# 設定ファイル読み込み
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/../_init/credentials"
. $CRED_DIR/secrets.txt
echo "PROJECT ID is ${PROJECT_ID}"

gcloud functions deploy qa-main --source $SCRIPT_DIR/deploy --set-env-vars env=qa,projectID=${PROJECT_ID},app_client_id=${QA_APP_CLIENT_ID},app_client_secret=${QA_APP_CLIENT_SECRET} --entry-point entrypoint --runtime python38 --trigger-http --allow-unauthenticated