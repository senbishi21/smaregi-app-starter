#!/bin/bash
# ./deploy.sh

# 設定ファイル読み込み
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/../_init/credentials"
. $CRED_DIR/secrets.txt
echo "PROJECT ID is ${PROJECT_ID}"

gcloud functions deploy <your function name>\
 --source $SCRIPT_DIR/deploy\
 --set-env-vars <your run-time env setting>\
 --entry-point <your function entry point>\
 --memory 256mb
 --runtime python38 --region asia-northeast1 --trigger-http --allow-unauthenticated


