from time import sleep, time
from QcloudApi.qcloudapi import QcloudApi
import random
import base64
import hashlib
import hmac
import json
import requests
from common import settings
from common.log import logger

secret_id = settings.SECRET_ID
secret_key = settings.SECRET_KEY
endpoint = "cvm.tencentcloudapi.com"
lb_name = "aketest{}".format(random.randint(0, 1000))


def get_string_to_sign(method, endpoint, params):
    s = method + endpoint + "/?"
    query_str = "&".join("%s=%s" % (k, params[k]) for k in sorted(params))
    return s + query_str


def sign_str(key, s, method):
    key = str(base64.b64decode(key), encoding="utf-8")
    hmac_str = hmac.new(key.encode("utf8"), s.encode("utf8"), method).digest()
    return base64.b64encode(hmac_str)


def create_instance(num):
    params = {
        "Action": "RunInstances",
        # "Placement.Zone": "ap-beijing-3",
        "Placement.ProjectId": 1126842,
        # "Region": "ap-beijing",
        # "VirtualPrivateCloud.VpcId": "vpc-366ds668",
        # "VirtualPrivateCloud.SubnetId": "subnet-pfdj7bg5",
        "ImageId": "img-8toqc6s3",  # centos7.4
        # "InstanceType": "S2.LARGE8",
        "InstanceCount": num,
        "SystemDisk.DiskType": "CLOUD_PREMIUM",
        "SystemDisk.DiskSize": 50,
        "DataDisks.0.DiskType": "CLOUD_PREMIUM",
        "DataDisks.0.DiskSize": 50,
        "InstanceName": "AkePublicDeploy-DT",
        "LoginSettings.Password": "07Apples",
        # "SecurityGroupIds.0": "sg-52hnrp2p",
        "Version": "2017-03-12",
        "HostName": "node",
        "InternetAccessible.InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
        "InternetAccessible.InternetMaxBandwidthOut": 1,
        "InternetAccessible.PublicIpAssigned": True,
        "TagSpecification.0.ResourceType": "instance",
        "TagSpecification.0.Tags.0.Key": "Group",
        "TagSpecification.0.Tags.0.Value": "QA",
        "UserData": "IyEvYmluL2Jhc2gKeXVtIGluc3RhbGwgLXkgc3NocGFzcwo=",
        "Timestamp": int(time()),
        "Nonce": random.randint(0, 1000),
        "SecretId": secret_id
    }
    if settings.ENV == "Staging":
        params.update({
            "Placement.Zone": "ap-beijing-3",
            "Region": "ap-beijing",
            "InstanceType": "S2.LARGE8",
            "VirtualPrivateCloud.VpcId": "vpc-366ds668",
            "VirtualPrivateCloud.SubnetId": "subnet-pfdj7bg5",
            "SecurityGroupIds.0": "sg-52hnrp2p"
        })
    elif settings.ENV == "private":
        params.update({
            "Placement.Zone": "ap-chongqing-1",
            "Region": "ap-chongqing",
            "InstanceType": "S3.LARGE8",
            "VirtualPrivateCloud.VpcId": "vpc-c9el9wfx",
            "VirtualPrivateCloud.SubnetId": "subnet-6ohk5y8a",
            "SecurityGroupIds.0": "sg-046r9ija"
        })
    else:
        return {"success": False, "message": "ENV is not Staging or private,can not create vm to deploy region"}
    s = get_string_to_sign("GET", endpoint, params)
    params["Signature"] = sign_str(secret_key, s, hashlib.sha1)
    logger.info("start to create qcloud vm")
    res = requests.get("https://" + endpoint, params=params)
    instances_id = []
    instances_id += res.json()['Response'].get("InstanceIdSet")
    if not instances_id:
        return {"success": False, "message": "create qcloud vm failed: {}".format(res.text)}
    logger.info("create vm success, but need to sleep 200s")
    sleep(200)
    return {"success": True, "instances_id": instances_id, "message": "create qcloud vm over"}


def get_instance(instances_id):
    params = {
        "Action": "DescribeInstances",
        "Version": "2017-03-12",
        # "Region": "ap-beijing",
        "SecretId": secret_id,
        "Timestamp": int(time()),
        "Nonce": random.randint(0, 1000),
    }
    if settings.ENV == "Staging":
        params.update({"Region": "ap-beijing"})
    elif settings.ENV == "private":
        params.update({"Region": "ap-chongqing"})
    else:
        pass
    for i in range(0, len(instances_id)):
        params.update({"InstanceIds." + str(i): str(instances_id[i])})
    s = get_string_to_sign("GET", endpoint, params)
    params["Signature"] = sign_str(secret_key, s, hashlib.sha1)
    res = requests.get("https://" + endpoint, params=params)
    if "InstanceSet" in res.json()['Response']:
        private_ips = []
        public_ips = []
        instances_info = res.json()['Response']['InstanceSet']
        for instance_info in instances_info:
            private_ips.append(str(instance_info['PrivateIpAddresses'][0]))
            public_ips.append(str(instance_info['PublicIpAddresses'][0]))
        return {"success": True, "private_ips": private_ips, "public_ips": public_ips,
                "message": "describe qcloud vm over"}
    return {"success": False, "message": "get qcloud vm info failed:{}".format(res.text)}


def destroy_instance(instances_id):
    params = {
        "Action": "TerminateInstances",
        "Version": "2017-03-12",
        # "Region": "ap-beijing",
        "SecretId": secret_id,
        "Timestamp": int(time()),
        "Nonce": random.randint(0, 1000),
    }
    if settings.ENV == "Staging":
        params.update({"Region": "ap-beijing"})
    elif settings.ENV == "private":
        params.update({"Region": "ap-chongqing"})
    else:
        pass
    for i in range(0, len(instances_id)):
        params.update({"InstanceIds." + str(i): str(instances_id[i])})
    s = get_string_to_sign("GET", endpoint, params)
    params["Signature"] = sign_str(secret_key, s, hashlib.sha1)
    res = requests.get("https://" + endpoint, params=params)
    if "TaskId" not in res.json()['Response']:
        return {"success": False, "message": "delete qcloud vm failed,please check it"}
    return {"success": True, "message": "delete qcloud vm over"}


def init_qcloud_lb():
    module = 'lb'
    config = {
        'Region': 'ap-beijing',
        'secretId': secret_id,
        'secretKey': str(base64.b64decode(secret_key), encoding="utf-8"),
        'method': 'GET',
        'SignatureMethod': 'HmacSHA1',
        'Version': '2017-03-12'
    }
    return QcloudApi(module, config)


def create_lb():
    action = 'CreateLoadBalancer'
    service = init_qcloud_lb()
    action_params = {
        "projectId": "1126842",
        "forward": 1,
        "loadBalancerType": "2",
        "loadBalancerName": lb_name
    }
    if "Success" not in str(service.call(action, action_params)):
        return {"success": False, "message": "create lb failed"}
    return {"success": True, "message": "create lb success"}


def describe_lb():
    action = 'DescribeLoadBalancers'
    service = init_qcloud_lb()
    action_params = {
        "projectId": "1126842",
        "forward": 1,
        "loadBalancerType": "2",
        "loadBalancerName": lb_name
    }
    response = str(service.call(action, action_params), encoding="utf-8")
    lb_id = json.loads(response)['loadBalancerSet'][0]['loadBalancerId']
    return lb_id


def create_listener(lb_id):
    action = "CreateForwardLBFourthLayerListeners"
    service = init_qcloud_lb()
    action_params = {
        "loadBalancerId": lb_id,
        "listeners.0.loadBalancerPort": 6443,
        "listeners.0.protocol": 2
    }
    response = str(service.call(action, action_params), encoding="utf-8")
    listenerid = json.loads(response)['listenerIds'][0]
    return listenerid


def bind_lb(instances_id):
    lb_id = describe_lb()
    listenerid = create_listener(lb_id)
    action = 'RegisterInstancesWithForwardLBFourthListener'
    service = init_qcloud_lb()
    action_params = {
        "projectId": "1126842",
        "forward": 1,
        "loadBalancerId": lb_id,
        "listenerId": listenerid
    }
    for i in range(0, len(instances_id)):
        action_params.update({"backends.{}.instanceId".format(i): str(instances_id[i])})
        action_params.update({"backends.{}.port".format(i): 6443})
    if "Success" not in str(service.call(action, action_params)):
        return {"success": False, "message": "bind lb failed"}
    return {"success": True, "message": "bind lb success"}


def delete_lb():
    lb_id = describe_lb()
    action = "DeleteLoadBalancers"
    service = init_qcloud_lb()
    action_params = {"loadBalancerIds.0": lb_id}
    service.call(action, action_params)
