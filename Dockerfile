FROM ubuntu:14.04

RUN apt-get update \
    && apt-get install -y \
        python-dev \
        libpq-dev \
        git \
        curl \
        expect \
    && curl https://bootstrap.pypa.io/get-pip.py | python

COPY requirements.txt .
RUN pip install -r /requirements.txt

RUN mkdir /var/log/mathilde

COPY run-local.sh .
RUN chmod +x /run-local.sh

WORKDIR /app

COPY . /app

CMD ["python", "/app/main.py"]


