import pytest
from test_case.integrations.ci_cd_integrations import Integrations


@pytest.mark.region
@pytest.mark.ci_cd
class TestCICDSuite(object):
    def setup_class(self):
        self.integration_tool = Integrations()

        self.integration_name = 'alauda-integration-{}'.format(self.integration_tool.region_name).replace('_', '-')

        self.description = "update instance"

        self.teardown_class(self)

    def teardown_class(self):
        integration_id = self.integration_tool.get_integration_id(self.integration_name)
        self.integration_tool.delete_integration(integration_id)

    def test_ci_cd(self):
        # create integration instance
        create_ret = self.integration_tool.create_integration('./test_data/integration/ci_cd/create_integration.yaml',
                                                              {"$INTEGRATION_NAME": self.integration_name})
        assert create_ret.status_code == 201, create_ret.text

        integration_id = create_ret.json()['id']

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, 'get integration instance status failed, Error code: {}, Response: {}' \
            .format(get_ret.status_code, get_ret.text)

        status = get_ret.json()['enabled']

        assert status, "integration instance status should be enabled, but disabled"

        # stop integration instance
        stop = self.integration_tool.stop_integration(integration_id,
                                                      './test_data/integration/ci_cd/stop_integration.yaml',
                                                      {"$PROJECT_NAME": self.integration_tool.params['project_name'],
                                                       "$INTEGRATION_ID": integration_id,
                                                       "$INTEGRATION_NAME": self.integration_name})
        assert stop.status_code == 200, "stop integration instance failed, Error code: {}, Response: {}" \
            .format(stop.status_code, stop.text)

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, 'get integration instance status failed, Error code: {}, Response: {}' \
            .format(get_ret.status_code, get_ret.text)

        status = get_ret.json()['enabled']

        assert not status, "integration instance status should be disabled, but enabled"

        # update integration instance
        update_ret = self.integration_tool.update_integration(integration_id,
                                                              './test_data/integration/ci_cd/update_integration.yaml',
                                                              {"$INTEGRATION_NAME": self.integration_name,
                                                               "$DESCRIPTION": self.description})
        assert update_ret.status_code == 200, "update integration instance failed, Error code: {}, Response: {}" \
            .format(update_ret.status_code, update_ret.text)

        # get integration instance status
        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 200, 'get integration instance status failed, Error code: {}, Response: {}' \
            .format(get_ret.status_code, get_ret.text)

        description = get_ret.json()['description']
        assert description == self.description, "update integration instance failed, description value should be {}, " \
                                                "but {}".format(self.description, description)

        # delete integration instance
        delete_ret = self.integration_tool.delete_integration(integration_id)
        assert delete_ret.status_code == 204, "delete integration instance failed, Error code: {}, Response: {}" \
            .format(delete_ret.status_code, delete_ret.text)

        get_ret = self.integration_tool.get_integration_detail(integration_id)
        assert get_ret.status_code == 404, "delete integration instance failed, Error code: {}, Response: {}" \
            .format(get_ret.status_code, get_ret.text)
