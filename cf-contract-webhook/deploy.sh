#!/bin/bash
# ./deploy.sh

# 設定ファイル読み込み
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/../_init/credentials"
. $CRED_DIR/secrets.txt
echo "PROJECT ID is ${PROJECT_ID}"

gcloud functions deploy qa-contract-webhook --source $SCRIPT_DIR/deploy --set-env-vars env=qa,projectID=${PROJECT_ID} --entry-point contract_update_webhook_receiver --runtime python38 --trigger-http --allow-unauthenticated