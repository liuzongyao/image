#!/usr/bin/env python
# -*- coding:utf-8 -*-
# import json
# dict = {'a': 1, 'b': 2, 'c': 3};
# print dict
# dict2 = {'c': 1, 'd': 2, 'e': 3};
# dict.update(dict2)
# print dict
#
#
#
# print type(dict.values())
# print dict.values()[0]
# if type(dict.values()) == list:
#     print "list"
#
# a=[]
# if a:
#     print('列表非空')
# else:
#     print('列表为空')
#
#
# aa = {u'editable': False, u'propagate': False, u'key': u'space', u'value': u'e2equota'}
# for k,v in aa.items():
#     print k,v
#
#
#



# import pytest
# def test_recursion_depth():
#     with pytest.raises(RuntimeError) as excinfo:
#         def f():
#             f()
#         f()
#     print excinfo.value
#     assert 'maximum recursion' not in str(excinfo.value)

import os
import json
import yaml

f = open("../config/env_staging.yaml")
env = yaml.load(f)
jsonfile=[]
for root, dirs, files in os.walk("../data_template1"):
    for filename in files:
        if os.path.splitext(file)[1] == '.json':
            jsonfile.append(os.path.join(root, file))


for filename in jsonfile:
    f1 = open(filename)
    jsondata = json.load(f1)
    for key, value in env.items():
        if jsondata.has_key(key):
            jsondata.update({key: value})
    f1.close()
    f2 = open(filename, 'w')
    json.dump(jsondata, f2, indent=2)  # indent 值代表格式化json文件
    f2.close()



