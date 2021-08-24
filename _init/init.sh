#!/bin/bash
# ./init.sh

# Google cloudの初期ログイン
gcloud auth login
read -p "Google CloudのプロジェクトIDを設定して下さい（必須）:" PROJECT_ID
echo "[$PROJECT_ID]を使用してセットアップを開始します"
gcloud config set project $PROJECT_ID

# Google Cloudの認証情報が入ったフォルダのパスを取得（どこで起動しても同じになるように）
SCRIPT_DIR=$(cd $(dirname $0); pwd)
CRED_DIR="${SCRIPT_DIR}/credentials"
mv ${SCRIPT_DIR}/credentials_template ${SCRIPT_DIR}/credentials
echo "PROJECT_ID=$PROJECT_ID" >> ${SCRIPT_DIR}/credentials/secrets.txt

# Google CloudのサービスアカウントのKeyを生成
SERVICE_ACCOUNT_ID=$(gcloud iam service-accounts list | tr ' ' '\n' | grep appspot)
if [ ! -e ${CRED_DIR}/service-account-key.json ]; 
then
	gcloud iam service-accounts keys create ${CRED_DIR}/service-account-key.json --iam-account $SERVICE_ACCOUNT_ID
fi

# クラウド管理に必要なAPIを有効にします
function enableAPI() {
	echo $1
	gcloud services list --enabled | grep $1
	if [ "$?" -eq 0 ] 
	then
		echo "$1 already enabled"
	else
	    echo "Enabling $1 API. Activation needs ~1min, please wait:)"
	    gcloud services enable $1
	fi
}

enableAPI "firestore.googleapis.com"
enableAPI "cloudfunctions.googleapis.com"
enableAPI "cloudbuild.googleapis.com"
enableAPI "clouderrorreporting.googleapis.com"
enableAPI "storage.googleapis.com"
sleep 20

# リージョンのデフォルトを東京(asia-northeast1)に
gcloud config set run/region asia-northeast1

# Firestoreには公式のCLIが存在しないため、Pythonで初期化
# ローカル環境を汚さないよう、Dockerで実装
docker build -t init-googlecloud-smaregi -f ${SCRIPT_DIR}/google-cloud-init/Dockerfile ${SCRIPT_DIR}/google-cloud-init &&\
docker run --name init-googlecloud-smaregi --rm -v $CRED_DIR:/tmp --env PROJECT_ID=$1 -it init-googlecloud-smaregi

# その後のインストラクション
echo "セットアップが終了しました。"
echo "1._init/credentials/secrets.txtに、スマレジ・Google Cloudの設定情報を入力し、cf-mainのフォルダで./run.shと./deploy.shを実行して下さい。"
echo "2.cf-mainをデプロイしたら、そのURLを_init/credentials/secrets.txtに記入して下さい。"
echo "3.その後、cf-redirect-OIDC, cf-contract-webhookで./deploy.shを実行して下さい"
echo "4.これですべて完了です！cf-mainのURLにアクセスしてみて下さい。"
