#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest.rest import alauda


def test_get_a_region_detail():
    resource_url = '/regions/' + alauda.namespace + '/' + alauda.region
    print resource_url
    response = alauda.get(resource_url)
    print type(response)
    # print response
    state = alauda.get_value(response, 'state')
    assert 'RUNNING' in state
