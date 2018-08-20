#!/usr/bin/env bash
docker rm -f e2etest
docker run -t --name e2etest \
	-v $(pwd):/app/ \
	-v $(pwd)/report:/app/report/ \
	index.alauda.cn/alaudaorg/api-test python /app/main.py