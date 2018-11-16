import pytest

from test_case.domain.domain import Domain


@pytest.mark.domain
@pytest.mark.ace
class TestDomainSuite(object):
    def setup_class(self):
        self.domain = Domain()
        self.domain_name = '*.test.{}'.format(self.domain.region_name).replace('_', '-')
        self.teardown_class(self)

    def teardown_class(self):
        domain_id = self.domain.get_domain_id(self.domain_name)
        self.domain.delete_domain(domain_id)

    @pytest.mark.BAT
    def test_domain(self):
        '''
        创建域名-更新域名-域名列表-搜索域名-删除域名
        :return:
        '''

        result = {"flag": True}
        # create domain
        createdomain_result = self.domain.create_domain("./test_data/domain/domain.json",
                                                        {"$domain_name": self.domain_name})
        assert createdomain_result.status_code == 201, "创建泛域名失败:{}".format(createdomain_result.text)
        domain_id = self.domain.get_domain_id(self.domain_name)

        # update domain
        update_result = self.domain.update_domain(domain_id, [self.domain.project_name])
        assert update_result.status_code == 204, "更新域名出错:{}".format(update_result.text)

        # list domain
        list_result = self.domain.list_domain()
        result = self.domain.update_result(result, list_result.status_code == 200, list_result.text)
        result = self.domain.update_result(result, self.domain_name in list_result.text, "域名列表：新建域名不在列表中")
        result = self.domain.update_result(result, self.domain.get_uuid_accord_name(list_result.json()['results'],
                                                                                    {"domain": self.domain_name},
                                                                                    "projects") == [
                                               self.domain.project_name], "域名列表：绑定项目不生效 {}".format(list_result.text))

        # search domain
        search_result = self.domain.search_domain(self.domain_name)
        result = self.domain.update_result(result, search_result.status_code == 200, search_result.text)
        result = self.domain.update_result(result, search_result.json()['count'] == 1, search_result.text)

        # delete domain
        delete_result = self.domain.delete_domain(domain_id)
        assert delete_result.status_code == 204, "删除域名失败：{}".format(delete_result.text)
        assert self.domain.check_exists(self.domain.get_common_domain_url(self.domain_name), 404)
        assert result['flag'], result
