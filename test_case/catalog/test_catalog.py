import pytest

from common.log import logger
from test_case.catalog.catalog import Catalog
from test_case.middleware.middleware import Middleware
from test_case.newapp.newapp import Newapplication


@pytest.mark.BAT
@pytest.mark.ace
@pytest.mark.flaky(reruns=2, reruns_delay=3)
class TestCatalogSuite(object):
    def setup_class(self):

        self.catalog = Catalog()
        self.middleware = Middleware()
        self.newapp = Newapplication()

        self.app_name = "e2e-mongodb-pri"
        self.namespace = self.middleware.global_info["$K8S_NAMESPACE"]

        self.git_name = "alauda-git-repository"
        self.update_git_displayname = "update-git-repository"
        self.svn_name = "alauda-svn-repository"
        self.upadte_svn_displayname = "update-svn-repository"

    def teardown_class(self):

        logger.info("开始清除应用目录数据")
        self.newapp.delete_newapp(self.namespace, self.app_name)
        self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.app_name), 404)
        if len(self.catalog.get_repository_list().json()) > 0:
            self.catalog.delete_repository(self.catalog.get_uuid_accord_name(self.catalog.get_repository_list().json()
                                                                             ["results"], {"name": self.git_name},
                                                                             "uuid"))
        if len(self.catalog.get_repository_list().json()) > 0:
            self.catalog.delete_repository(self.catalog.get_uuid_accord_name(self.catalog.get_repository_list().json()
                                                                             ["results"], {"name": self.svn_name},
                                                                             "uuid"))
        logger.info("清除完毕")

    @pytest.mark.repository_git
    def test_repository_git(self):

        '''
        添加应用目录模板仓库
        :return:
        '''

        result = {"flag": True}

        create_result = self.catalog.create_repository('./test_data/catalog/repository_git.json',
                                                       {'$repository_name': self.git_name})
        assert create_result.status_code == 201, "添加应用目录git模板仓库失败 {}".format(create_result.text)
        self.git_id = self.catalog.get_value(create_result.json(), 'uuid')
        logger.info("git模板仓库创建成功")

        '''
        获取模板仓库列表，列表中包含新建模板仓库
        '''
        repository_list = self.catalog.get_repository_list()
        result = self.catalog.update_result(result, repository_list.status_code == 200, "获取应用目录模板仓库列表失败")
        result = self.catalog.update_result(result, self.git_name in repository_list.text,
                                            "获取应用目录模板仓库列表失败:新建git模板仓库不在列表中")
        logger.info("列表中包含新建git模板仓库")

        '''
        获取模板仓库详细信息
        '''
        repository_status = self.catalog.get_repository_status(self.git_id, "SUCCESS")
        assert repository_status, "创建应用目录git模板仓库后，状态不是SUCCESS"
        logger.info("获取git模板仓库详情信息成功")

        '''
        更新模板仓库
        '''
        update_result = self.catalog.update_repository(self.git_id, './test_data/catalog/update_repository_git.json',
                                                       {'$display_name': self.update_git_displayname})
        assert update_result.status_code == 200, "更新应用目录git模板仓库失败 {}".format(update_result.text)
        result = self.catalog.update_result(result, self.update_git_displayname in update_result.text,
                                            "更新应用目录模板仓库失败：修改的显示名称与设置不一致")
        repository_status = self.catalog.get_repository_status(self.git_id, "SUCCESS")
        assert repository_status, "更新应用目录git模板仓库后，状态不是SUCCESS"
        logger.info("更新应用目录git模板仓库成功")

        '''
        同步模板仓库
        '''
        refresh_result = self.catalog.refresh_repository(self.git_id)
        assert refresh_result.status_code == 204, "应用目录同步模板仓库失败 {}".format(refresh_result.text)
        repository_status = self.catalog.get_repository_status(self.git_id, "SUCCESS")
        assert repository_status, "同步应用目录git模板仓库后，状态不是SUCCESS"
        logger.info("同步git模板仓库成功")
        assert result['flag'], result

    @pytest.mark.repository_svn
    def test_repository_svn(self):
        '''
        添加应用目录模板仓库
        :return:
        '''

        result = {"flag": True}

        create_result = self.catalog.create_repository('./test_data/catalog/repository_svn.json',
                                                       {'$repository_name': self.svn_name})
        assert create_result.status_code == 201, "添加应用目录svn模板仓库失败 {}".format(create_result.text)
        self.svn_id = self.catalog.get_value(create_result.json(), 'uuid')
        logger.info("模板仓库创建成功")

        '''
        获取模板仓库列表，列表中包含新建模板仓库
        '''
        repository_list = self.catalog.get_repository_list()
        result = self.catalog.update_result(result, repository_list.status_code == 200, "获取应用目录svn模板仓库列表失败")
        result = self.catalog.update_result(result, self.svn_name in repository_list.text,
                                            "获取应用目录svn模板仓库列表失败:新建模板仓库不在列表中")
        logger.info("列表中包含新建模板仓库")

        '''
        获取模板仓库详细信息
        '''
        repository_status = self.catalog.get_repository_status(self.svn_id, "SUCCESS")
        assert repository_status, "创建应用目录svn模板仓库后，状态不是SUCCESS"
        logger.info("获取详情信息成功")

        '''
        更新模板仓库
        '''
        update_result = self.catalog.update_repository(self.svn_id, './test_data/catalog/update_repository_svn.json',
                                                       {'$display_name': self.upadte_svn_displayname})
        assert update_result.status_code == 200, "更新应用目录svn模板仓库失败 {}".format(update_result.text)
        result = self.catalog.update_result(result, self.upadte_svn_displayname in update_result.text,
                                            "更新应用目录svn模板仓库失败：修改的显示名称与设置不一致")
        repository_status = self.catalog.get_repository_status(self.svn_id, "SUCCESS")
        assert repository_status, "更新应用目录svn模板仓库后，状态不是SUCCESS"
        logger.info("更新模板仓库成功")

        '''
        同步模板仓库
        '''
        refresh_result = self.catalog.refresh_repository(self.svn_id)
        assert refresh_result.status_code == 204, "应用目录同步模板仓库失败 {}".format(refresh_result.text)
        repository_status = self.catalog.get_repository_status(self.svn_id, "SUCCESS")
        assert repository_status, "同步应用目录模板仓库后，状态不是SUCCESS"
        logger.info("同步模板仓库成功")

        '''
        删除模板仓库
        '''
        delete_result = self.catalog.delete_repository(self.svn_id)
        result = self.catalog.update_result(result, delete_result.status_code == 200, "删除应用目录svn模板仓库失败")
        assert result['flag'], result
        logger.info("删除应用目录svn模板仓库成功")

    @pytest.mark.catalog_mongodb
    def test_catalog_mongodb(self):

        '''
        使用应用目录模板中的模板创建mongodb应用
        :return:
        '''

        result = {"flag": True}
        assert len(self.catalog.get_repository_list().json()) > 0, "应用没有创建出git仓库，没法创建mongodb应用"
        if len(self.catalog.get_repository_list().json()) > 0:
            repository_id = self.catalog.get_uuid_accord_name(self.catalog.get_repository_list().json()["results"],
                                                              {"name": self.git_name}, "uuid")

            templates_list = self.catalog.get_templates(repository_id)
            templates = self.catalog.get_value(templates_list.json(), 'results')
            template_id = ""
            for template in templates:
                template_name = template["name"]
                if "mongodb" == template_name:
                    template_id = template["uuid"]
                    break
            logger.info("获取应用目录mongodb模板的id：{}".format(template_id))
            mongodb_info = self.middleware.get_template_info(template_id)
            version_id = mongodb_info.json()["versions"][0]["uuid"]
            logger.info("获取到的mongodb的version id:{}".format(version_id))

            create_result = self.middleware.create_application('./test_data/catalog/catalog_mongodb.json',
                                                               {"$catalog_app_name": self.app_name,
                                                                "$template_id": template_id, "$version_id": version_id})
            assert create_result.status_code == 201, "创建mongodb失败 {}".format(create_result.text)
            logger.info("应用目录创建mongodb成功")

            app_id = create_result.json()["kubernetes"]["metadata"]["uid"]
            logger.info("创建mongodb成功，id是：{}".format(app_id))
            logger.info("创建mongodb成功，name是：{}".format(self.app_name))

            app_status = self.middleware.get_application_status(self.namespace, self.app_name, "Running")

            assert app_status, "创建应用后，验证应用状态出错：app: {} is not running".format(self.app_name)
            logger.info("mongodb的应用状态为：Running")

            # 删除应用
            delete_result = self.newapp.delete_newapp(self.namespace, self.app_name)
            assert delete_result.status_code == 204, "删除应用目录创建出的mongodb应用失败 {}".format(delete_result.text)
            self.newapp.check_exists(self.newapp.get_newapp_common_url(self.namespace, self.app_name), 404)
            assert result['flag'], True
