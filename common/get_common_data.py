import os
from pathlib import Path
from common.base_request import Common
from common.utils import retry


def target_file():
    path_list = [os.path.dirname(os.getcwd()), os.getcwd()]
    for path in path_list:
        target_file = os.path.join(path, 'common', 'settings.py')
        path = Path(target_file)
        if path.exists() and path.is_file():
            return target_file


def input_file(content):
    """
    :param content: str
    :return:
    """
    file = target_file()
    file_path = os.path.join(os.path.dirname(file), '../temp_data')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    new_file = os.path.join(file_path, 'temporary.py')

    with open(file, 'r') as read:
        with open(new_file, 'w+') as write:
            for line in read:
                write.writelines(line)
            write.writelines(content)


class CommonData(Common):
    def __init__(self):
        super(CommonData, self).__init__()
        self.common = ''
        self.get_region_data()
        self.get_build_endpontid()
        self.get_load_balance_info()
        input_file(self.common)

    @retry()
    def get_region_data(self):
        """
        :return: 给self.region_data赋值集群信息  给self.region_id赋值集群ID
        """
        response = self.send(method="GET", path="/v1/regions/{}/{}/".format(self.account, self.region_name))
        assert response.status_code == 200, response.json()
        self.region_data = response.json()
        self.region_id = self.get_value(self.region_data, "id")
        self.common = self.common + 'REGION_ID = "{}"\n'.format(self.region_id)

    @retry()
    def get_build_endpontid(self):
        """
        :return: 给self.build_endpoint赋值构建的集群ID
        """
        response = self.send(method="GET", path="/v1/private-build-endpoints/{}".format(self.account))
        assert response.status_code == 200, response.text
        for content in response.json():
            if content['region_id'] == self.region_id:
                self.build_endpointid = content['endpoint_id']
                self.common = self.common + 'BUILD_ENDPOINTID = "{}"\n'.format(self.build_endpointid)
                break

    @retry()
    def get_load_balance_info(self):
        response = self.send(method='GET', path='/v1/load_balancers/{}?region_name={}'
                                                '&detail=false&service_id=&frontend=false'.format(
                                                    self.account, self.region_name))
        assert response.status_code == 200, response.text
        contents = response.json()
        for content in contents:
            if "name" in content:
                self.common = self.common + 'HAPROXY_NAME = "{}"\n'.format(content['name'])
                self.common = self.common + 'HAPROXY_IP = "{}"\n'.format(content['address'])
                break
