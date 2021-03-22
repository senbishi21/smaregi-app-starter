FROM python:3.8
RUN pip install flask jinja2 requests

COPY deploy/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY deploy/*.py /app/
WORKDIR /app

ENV GOOGLE_APPLICATION_CREDENTIALS="/tmp/service-account-key.json"

CMD ["python", "main.py"]
# CMD sleep 1d