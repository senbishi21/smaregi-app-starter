FROM python:3.8
RUN pip install firebase-admin

COPY main.py /app/
WORKDIR /app

ENV GOOGLE_APPLICATION_CREDENTIALS="/tmp/service-account-key.json"

CMD python main.py --project_id=$PROJECT_ID
# CMD sleep 1d