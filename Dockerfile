FROM bitnami/python:3-prod

RUN install_packages vim curl ssh

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r /requirements.txt

COPY run-local.sh .
RUN chmod +x /run-local.sh

WORKDIR /app
COPY . /app

CMD ["python", "/app/main.py"]

