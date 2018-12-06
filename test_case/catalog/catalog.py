import sys
from time import sleep

from common.base_request import Common
from common.log import logger


class Catalog(Common):

    # 模板添加、更新、删除、详细信息
    def get_repository_url(self, uuid=''):
        return "v2/catalog/template_repositories/{}".format(uuid)

    # 模板同步
    def get_repository_refresh_url(self, uuid):
        return "v2/catalog/template_repositories/{}/refresh".format(uuid)

    # 根据模板仓库id获取所用模板的id
    def get_template_url(self, uuid):
        return "v2/catalog/templates?repository_uuid={}".format(uuid)

    '''
    应用目录：增加/修改/删除/查询/同步模板，查询模板列表
    '''

    def get_repository_list(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_repository_url()
        return self.send(method='get', path=url)

    def create_repository(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_repository_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def get_repository_detail(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_repository_url(uuid)
        return self.send(method='get', path=url)

    def update_repository(self, uuid, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_repository_url(uuid)
        data = self.generate_data(file, data)
        return self.send(method='put', path=url, data=data)

    def delete_repository(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_repository_url(uuid)
        return self.send(method='delete', path=url)

    def refresh_repository(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_repository_refresh_url(uuid)
        return self.send(method='put', path=url)

    def get_templates(self, uuid):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_template_url(uuid)
        return self.send(method='get', path=url)

    '''
    等待仓库模板倒入成功，状态为"SUCCESS"
    '''

    def get_repository_status(self, uuid, expect_status):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        cnt = 0
        flag = False
        while cnt < 60 and not flag:
            cnt += 1
            detail_result = self.get_repository_detail(uuid)
            assert detail_result.status_code == 200, "获取应用目录模板仓库详情信息失败"

            if expect_status in detail_result.text:
                flag = True
                break
            sleep(5)

        return flag
