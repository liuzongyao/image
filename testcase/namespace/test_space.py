from rest.rest import Alauda

alauda = Alauda()

print alauda.header


def test_space_list_for_namespace():
    response = alauda.get('/spaces/testorg001')
    print type(response)
    print response
    assert 'running' in response




