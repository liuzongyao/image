import requests
import json
header = {'Content-Type':'application/json','Authorization': 'Token ad2ba8a3c2fa7637179c9854107dd55e67e24f7c'}

jsondata = json.load(open('/Users/zliu/api/data_template/start_build.json'))  # dic
data = json.dumps(jsondata)

# payload = {"build_config_name": "demo"}
#
# data = json.dumps(payload)

r = requests.post('https://api-staging.alauda.cn/v1/private-builds/testorg001/', data=data,headers=header)

print r.status_code
json_response = json.loads(r.text)
print json_response