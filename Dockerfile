FROM bitnami/python:3.6.5-prod
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN install_packages vim curl ssh

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r /requirements.txt

WORKDIR /app
COPY . /app

CMD ["python", "/app/main.py"]

