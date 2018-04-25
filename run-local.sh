#!/usr/bin/env bash
docker rm -f vipercd
docker run -t --name vipercd -v $(pwd):/app/ -v $(pwd)/report:/app/report/ index.alauda.cn/alaudaorg/pytest:latest python /app/main1.py
