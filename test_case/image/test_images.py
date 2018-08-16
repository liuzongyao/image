import pytest
from test_case.image.image import Image


@pytest.mark.region
@pytest.mark.image
class TestImageSuite(object):
    def setup_class(self):
        self.image_tool = Image()

        self.reg_project_name = 'alauda-reg-project-{}'.format(self.image_tool.registry_name)
        self.update_repo = "update daemon"
        self.repo_name = 'alauda-repo-{}'.format(self.image_tool.registry_name)

        self.image_tool.delete_repo(self.repo_name, reg_project_name=self.reg_project_name)
        self.image_tool.delete_reg_project(self.reg_project_name)

    def teardown_class(self):
        self.image_tool.delete_repo(self.repo_name, reg_project_name=self.reg_project_name)
        self.image_tool.delete_reg_project(self.reg_project_name)

    def test_image(self):
        # create registry project
        create_reg_ret = self.image_tool.create_reg_project('./test_data/image/create_reg_project.yaml',
                                                            {"$REG_PROJECT_NAME": self.reg_project_name})
        assert create_reg_ret.status_code == 201, create_reg_ret.text

        # get registry project
        get_reg_ret = self.image_tool.get_reg_project(self.reg_project_name)
        assert get_reg_ret

        # create repo
        create_repo_ret = self.image_tool.create_repo('./test_data/image/create_repo.yaml',
                                                      {"$REPO_IMAGE": self.repo_name},
                                                      reg_project_name=self.reg_project_name)
        assert create_repo_ret.status_code == 201, create_repo_ret.text

        # get repo
        get_repo_ret = self.image_tool.get_repo_detail(self.repo_name, reg_project_name=self.reg_project_name)
        assert get_repo_ret.status_code == 200, get_repo_ret.text

        # update repo
        update_repo_ret = self.image_tool.update_repo(self.repo_name, './test_data/image/update_repo.yaml',
                                                      {"$UPDATE_REPO": self.update_repo},
                                                      reg_project_name=self.reg_project_name)
        assert update_repo_ret.status_code == 200, update_repo_ret.text
        # get repo detail after update
        get_repo_detail = self.image_tool.get_repo_detail(self.repo_name, reg_project_name=self.reg_project_name)
        assert get_repo_detail.status_code == 200, get_repo_detail.text
        # verify the update value
        content = get_repo_detail.json()
        ret = self.image_tool.get_value(content, 'full_description')
        assert ret == self.update_repo

        # delete repo
        delete_repo_ret = self.image_tool.delete_repo(self.repo_name, reg_project_name=self.reg_project_name)
        assert delete_repo_ret.status_code == 204, delete_repo_ret.text

        # verify delete result
        get_repo_ret = self.image_tool.get_repo_detail(self.repo_name, reg_project_name=self.reg_project_name)
        assert get_repo_ret.status_code == 404, "delete repo failed, Error code:{}, Response: {}".format(
            get_repo_ret.status_code, get_repo_ret.text)

        # delete registry project
        delete_reg_ret = self.image_tool.delete_reg_project(self.reg_project_name)
        assert delete_reg_ret.status_code == 204, delete_reg_ret.text

        # verify delete result
        get_reg_project_ret = self.image_tool.get_reg_project(self.reg_project_name)
        assert get_reg_project_ret is False, "delete registry project failed"
