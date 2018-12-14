import pytest
import json
from test_case.resources_manage.resource_list import ResourceList


@pytest.mark.BAT
@pytest.mark.ace
@pytest.mark.flaky(reruns=2, reruns_delay=3)
class TestResourceSuite(object):
    def test_resource_list(self):
        result = {"flag": True}
        resource_client = ResourceList()
        all_type_content = resource_client.list_resources()
        result = resource_client.update_result(result, all_type_content.status_code == 200, all_type_content.text)
        get_resource_type = resource_client.get_resource_type_list(all_type_content.json())
        resource_list = set(json.loads(resource_client.generate_data('./test_data/resource_list/all_resources.json')))
        result = resource_client.update_result(result, resource_list.issubset(get_resource_type), "管理视图资源列表不匹配")
        assert result["flag"], result