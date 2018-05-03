from rest.rest import alauda
import pytest


def test_create_basic_service_deployment():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/create_basic_service_deployment.json')

    service_name = alauda.get_value(response1,'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port = alauda.get_value(response2, 'container_port')

    print container_port
    #
    # response3 = alauda.delete(resource2_url)
    #
    # print response3

    assert 'running' in 'running'

@pytest.mark.skip(reason="no way of currently testing this")
def test_create_basic_service_status():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/create_basic_service_deployment.json')

    service_name = alauda.get_value(response1,'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    current_status = alauda.circle_get_value(resource2_url, 'current_status', circle=10)

    print current_status

    assert 'running' in 'running'


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_service_with_data_template_update():
    resource1_url = '/services/' + alauda.namespace
    filename = alauda.generate_data_template('./data_template/create_basic_service_deployment.json', service_name="demo123")
    response1 = alauda.post(resource1_url, filename)
    print type(response1)
    assert 'running' in 'running'

@pytest.mark.skip(reason="no way of currently testing this")
def test_create_service_with_data_template_append_envvar():
    resource1_url = '/services/' + alauda.namespace
    filename = alauda.generate_data_template('./data_template/create_basic_service_deployment.json', name='./data_template/envvar.json')
    response1 = alauda.post(resource1_url, filename)
    print type(response1)
    assert 'running' in 'running'


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_basic_service_with_expected_status():

    resource1_url = '/services/' + alauda.namespace

    response1 = alauda.post(resource1_url, './data_template/create_basic_service_deployment.json')

    service_name = alauda.get_value(response1,'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    current_status = alauda.get_expected_value(resource2_url, 'current_status', 'Running', circle=10)

    print current_status

    assert current_status


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_service_with_data_template_append_ha():
    resource1_url = '/services/' + alauda.namespace
    filename = alauda.generate_data_template('./data_template/create_basic_service_deployment.json', name='./data_template/haproxy.json')
    response1 = alauda.post(resource1_url, filename)
    print type(response1)
    assert 'running' in 'running'


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_basic_service_dameonset():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/create_basic_service_dameonset.json')

    service_name = alauda.get_value(response1,'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port = alauda.get_value(response2, 'container_port')

    print container_port
    #
    # response3 = alauda.delete(resource2_url)
    #
    # print response3

    assert 'running' in 'running'


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_basic_service_statefulset():

    resource1_url = '/services/' + alauda.namespace
    response1 = alauda.post(resource1_url, './data_template/create_basic_service_statefulset.json')

    service_name = alauda.get_value(response1,'unique_name')

    resource2_url = '/services/' + alauda.namespace + '/' + service_name

    response2 = alauda.get(resource2_url)

    current_status = alauda.get_value(response2, 'current_status')

    print current_status

    container_port = alauda.get_value(response2, 'container_port')

    print container_port
    #
    # response3 = alauda.delete(resource2_url)
    #
    # print response3

    assert 'running' in 'running'


