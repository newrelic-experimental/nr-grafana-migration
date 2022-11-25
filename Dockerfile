FROM python:3.9-slim
LABEL "app"="nr-grafana-migration"
ENV PYTHONUNBUFFERED=0

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt

# Copy function code
COPY *.py /app/
COPY src/ /app/src


CMD ["python", "-u", "main.py"]
