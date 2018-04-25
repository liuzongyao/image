from rest.rest import Alauda
import pytest

alauda = Alauda()
print alauda.header

def test_get_a_region_detail():
    resource_url = '/regions/testorg001/' + alauda.region
    response = alauda.get(resource_url)
    #print type(response)
    #print response
    state = alauda.get_value(response,'state')
    assert 'RUNNING' in state

def test_bugs():
    with pytest.raises(ValueError, unknown='foo'):
        raise ValueError
