#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest.rest import alauda

print alauda.header


def test_space_list_for_namespace():
    resource_url = '/spaces/' + alauda.namespace
    print resource_url
    response = alauda.get(resource_url)
    print type(response)
    print response
    assert 'running' in response
