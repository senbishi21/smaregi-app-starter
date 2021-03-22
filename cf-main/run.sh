#!/bin/bash
# ./run.sh

##### SETTINGS #####
IMAGE_NAME=smaregi-main
PORT_NUM=4010

# Google Cloudの認証情報が入ったフォルダのパスを取得（どこで起動しても同じになるように）
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/../_init/credentials"

. $CRED_DIR/secrets.txt
echo "PROJECT ID is ${PROJECT_ID}"
echo "LOCAL ID is ${LOCAL_CONTRACT_ID}"
################


docker build -t $IMAGE_NAME . &&\
echo "launching container:　"$IMAGE_NAME" port: "$PORT_NUM &&\
open http://localhost:$PORT_NUM &&\
docker run -p $PORT_NUM:8080 --env projectID=${PROJECT_ID} --env app_client_id=${QA_APP_CLIENT_ID} --env app_client_secret=${QA_APP_CLIENT_SECRET} --env local_contract_id=${LOCAL_CONTRACT_ID} -v $CRED_DIR:/tmp --name $IMAGE_NAME --rm -it $IMAGE_NAME
