#!coding=utf-8
import sys
import json
# 读取数据
with open('/etc/docker/daemon.json', 'r') as f:
    data = json.load(f)
    for i in range(1, len(sys.argv)):
        if sys.argv[i] not in data['insecure-registries']:
            data['insecure-registries'].append(sys.argv[i])

# 写入 JSON 数据
with open('/etc/docker/daemon.json', 'w') as f:
    json.dump(data, f)
