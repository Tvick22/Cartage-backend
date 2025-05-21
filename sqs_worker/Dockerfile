FROM docker.io/python:3.12.8

WORKDIR /sqs_worker_live

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY worker.py .

CMD ["python", "-u", "worker.py"]