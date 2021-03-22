FROM python:3.8
RUN pip install flask

COPY deploy/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY deploy/main.py /app/
WORKDIR /app

ENV GOOGLE_APPLICATION_CREDENTIALS="/tmp/service-account-key.json"

CMD ["python", "main.py"]
# CMD sleep 1d