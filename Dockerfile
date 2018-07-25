FROM bitnami/python:3.6.5-prod

RUN install_packages vim curl ssh

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r /requirements.txt

WORKDIR /app
COPY . /app

CMD ["python", "/app/main.py"]

