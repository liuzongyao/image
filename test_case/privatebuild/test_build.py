import pytest
from test_case.privatebuild.build import PrivateBuild


@pytest.mark.region
@pytest.mark.privatebuild
class TestPrivateBuildTestSuit(object):
    def setup_class(self):
        self.client = PrivateBuild()
        self.svn_build_name = "alauda-svn-{}".format(self.client.region_name)
        self.dockerfile_name = "alauda-dockerfile-{}".format(self.client.region_name)
        self.teardown_class(self)

    def teardown_class(self):
        self.client.delete_dockerfile(self.dockerfile_name)
        self.client.delete_build(self.svn_build_name)

    def test_svn_build(self):
        """
        获取CI镜像-预览YAML-上传Dockerfile-预览Dockerfile-更新Dockerfile-删除Dockerfile-创建构建-检查创建事件-获取构建配置列表
        -触发构建-构建日志-检查触发事件-检查版本-获取历史列表-删除构建历史-删除构建配置
        """
        result = {"flag": True}
        # 获取ci镜像
        ret_ci = self.client.get_ci_image()
        self.client.update_result(result, ret_ci.status_code == 200, "获取CI镜像出错:{}".format(ret_ci.text))
        actual_ci_language = ["golang", "java", "java", "java", "python", "golang"]
        actual_ci_runtime = ["1.7", "openjdk7", "oraclejdk7", "oraclejdk8", "2.7", "1.6"]
        expect_ci_language = []
        expect_ci_runtime = []
        for content in ret_ci.json():
            expect_ci_language.append(content['language'])
            expect_ci_runtime.append(content['runtime'])
        flag = (actual_ci_language.sort() == expect_ci_language.sort() and actual_ci_runtime.sort() ==
                expect_ci_runtime.sort())
        self.client.update_result(result, flag, "获取CI镜像出错")
        # 预览YAML
        ret_yaml = self.client.get_ci_yaml("./test_data/build/ci_env.json")
        self.client.update_result(result, ret_yaml.status_code == 200, "预览YAML出错:{}".format(ret_yaml.text))
        # 上传Dockerfile
        files = {"dockerfile": "FROM index.alauda.cn/alauda/hello-world:latest"}
        ret_upload = self.client.upload_dockerfile({"name": self.dockerfile_name}, files)
        self.client.update_result(result, ret_upload.status_code == 201, "上传dockerfile出错:{}".format(ret_upload.text))
        # 预览Dockerfile
        ret_dockerfile = self.client.get_dockerfile_list()
        self.client.update_result(result, ret_dockerfile.status_code == 200, "预览dockerfile出错:{}".format(
            ret_dockerfile.text))
        self.client.update_result(result, self.client.get_value(ret_dockerfile.json(), "0.name") ==
                                  self.dockerfile_name, "预览dockerfile出错")
        # 更新Dockerfile
        ret_update = self.client.update_dockerfile(self.dockerfile_name, {"name": self.dockerfile_name}, files)
        self.client.update_result(result, ret_update.status_code == 204, "更新Dockerfile出错:{}".format(ret_update.text))
        # 删除dockerfile
        ret_del = self.client.delete_dockerfile(self.dockerfile_name)
        self.client.update_result(result, ret_del.status_code == 204, "删除dockerfile出错:{}".format(ret_del.text))
        # 创建构建
        ret_create = self.client.create_build("./test_data/build/svn_build.json", {"$NAME": self.svn_build_name})
        assert ret_create.status_code == 201, "创建构建出错:{}".format(ret_create.text)
        config_id = ret_create.json()["config_id"]
        # 检查创建事件
        event_flag = self.client.get_build_event(config_id, "create")
        self.client.update_result(result, event_flag, "获取构建创建事件出错")
        # 获取构建配置列表
        ret_list = self.client.get_build_list()
        self.client.update_result(result, ret_list.status_code == 200, "获取构建列表出错:{}".format(ret_update.text))
        build_names = self.client.get_value_list(ret_list.json(), "results.name")
        self.client.update_result(result, self.svn_build_name in build_names, "获取构建列表出错")
        # 触发构建
        ret_trigger = self.client.trigger_build(config_id)
        assert ret_trigger.status_code == 201, "触发构建出错{}".format(ret_trigger.text)
        history_id = ret_trigger.json()["build_id"]
        # 检查触发事件
        event_flag = self.client.get_build_event(history_id, "create")
        self.client.update_result(result, event_flag, "获取构建触发事件出错")
        ret_status = self.client.get_build_status(history_id)
        assert ret_status, "触发构建出错：build failed"
        # 构建日志
        ret_log = self.client.get_build_log(history_id)
        result = self.client.update_result(result, ret_log, "获取构建日志出错：get build log")
        # 删除构建历史

        # 删除构建配置
        ret_del = self.client.delete_build(self.svn_build_name)
        assert ret_del.status_code == 204, ret_del.text
        assert result["flag"], result
