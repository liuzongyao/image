from rest.rest import Alauda
import pytest

alauda = Alauda()

print alauda.header


@pytest.mark.skip(reason="no way of currently testing this")
def test_create_build():
    response = alauda.post('/private-build-configs/testorg001','./data_template/build_config.json')
    print type(response)
    print response
    assert 'running' in response


def test_start_build():
    response = alauda.post('/private-builds/testorg001','./data_template/start_build.json')
    print type(response)
    print response
    assert 'running' in response


