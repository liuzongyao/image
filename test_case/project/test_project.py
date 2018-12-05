from test_case.project.project import Project


class TestProjectSuite(object):
    def setup_class(self):
        self.project = Project()
        self.project_name = "alauda-project-{}".format(self.project.region_name)
        self.display_name = "project_test"
        self.teardown_class(self)

    def teardown_class(self):
        self.project.delete_project_role(self.project_name)
        self.project.delete_project(self.project_name)

    def test_project(self):
        """
        创建项目-获取项目列表-更新项目-获取项目详情-删除项目
        """
        final_result = {"flag": True}

        ret_create = self.project.create_project('./test_data/project/project.yml', {"$project": self.project_name})
        assert ret_create.status_code == 201, "创建项目失败:{}".format(ret_create.text)

        ret_list = self.project.get_project_list()
        self.project.update_result(final_result, ret_list.status_code == 200, "获取项目列表失败：{}".format(ret_list.text))
        self.project.update_result(final_result,
                                   self.project_name in self.project.get_value_list(ret_list.json(), "name"),
                                   "新建项目不在项目列表内")

        ret_update = self.project.update_project(self.project_name, {"display_name": self.display_name})
        self.project.update_result(final_result, ret_update.status_code == 204, "更新项目失败:{}".format(ret_update.text))

        ret_detail = self.project.get_project(self.project_name)
        self.project.update_result(final_result, ret_detail.status_code == 200, "获取项目详情失败：{}".format(ret_detail.text))
        self.project.update_result(final_result, self.display_name in ret_detail.text, "获取项目详情失败")

        ret_role = self.project.get_project_role(self.project_name)
        self.project.update_result(final_result, len(ret_role) == 2, "项目中应该有两个角色，实际：{}".format(len(ret_role)))

        # ret_del = self.project.delete_project(self.project_name)
        # self.project.update_result(final_result, ret_del.status_code == 409,
        #                            "期望删除项目返回409，结果：{}".format(ret_del.status_code))
        #
        # self.project.delete_project_role(self.project_name)

        ret_del = self.project.delete_project(self.project_name)
        self.project.update_result(final_result, ret_del.status_code == 204,
                                   "204，结果：{}".format(ret_del.status_code))

        assert final_result.get("flag"), final_result
