#!/bin/bash
# ./run.sh

##### SETTINGS #####
IMAGE_NAME=smaregi-contract-webhook
PORT_NUM=3334

# Google Cloudの認証情報が入ったフォルダのパスを取得（どこで起動しても同じになるように）
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/../_init/credentials"
################


docker build -t $IMAGE_NAME . &&\
echo "launching container:　"$IMAGE_NAME" port: "$PORT_NUM &&\
docker run -p $PORT_NUM:8080 -v $CRED_DIR:/tmp --name $IMAGE_NAME --rm -it $IMAGE_NAME
