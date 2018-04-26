from rest.rest import alauda
import pytest


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_build():
    resource_url = '/private-build-configs/' + alauda.namespace
    response = alauda.post(resource_url, './data_template/build_config.json', )
    print type(response)
    print response
    assert 'running' in 'running'


def test_new_name_build():
    resource_url = '/private-build-configs/' + alauda.namespace
    response = alauda.post(resource_url, './data_template/build_config.json', name='demo12345')
    print type(response)
    print response
    assert 'running' in 'running'


def test_start_new_name_build():
    resource_url = '/private-builds/' + alauda.namespace
    response = alauda.post(resource_url, './data_template/start_build.json')
    print type(response)
    print response
    assert 'running' in 'running'


def test_start_build():
    resource_url = '/private-builds/' + alauda.namespace
    response = alauda.post(resource_url, './data_template/start_build.json')
    print type(response)
    print response
    assert 'running' in 'running'
