import sys

from common import settings
from common.base_request import Common
from common.log import logger


class Volume(Common):
    def get_list_volume_url(self):
        return 'v1/storage/{}/volumes?region_id={}'.format(settings.ACCOUNT, self.global_info["$REGION_ID"])

    def get_drivers_url(self):
        return 'v1/storage/{}/{}/drivers/'.format(settings.ACCOUNT, settings.REGION_NAME)

    def get_create_volume_url(self):
        return 'v1/storage/{}/volumes'.format(settings.ACCOUNT)

    def get_common_volume_url(self, volume_id):
        return 'v1/storage/{}/volumes/{}'.format(settings.ACCOUNT, volume_id)

    def list_volume(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_list_volume_url()
        return self.send(method='get', path=url)

    def list_drivers(self):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_drivers_url()
        return self.send(method='get', path=url)

    def create_volume(self, file, data):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_create_volume_url()
        data = self.generate_data(file, data)
        return self.send(method='post', path=url, data=data)

    def get_volume_detail(self, volume_id):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_volume_url(volume_id)
        return self.send(method='get', path=url)

    def delete_volume(self, volume_id):
        logger.info(sys._getframe().f_code.co_name.center(50, '*'))
        url = self.get_common_volume_url(volume_id)
        return self.send(method='delete', path=url)

    def get_volume_id_from_list(self, volume_name):
        response = self.list_volume()
        if response.status_code != 200:
            return ""
        volume_id = ""
        volumes = response.json().get("volumes")
        for volume in volumes:
            if volume.get("name") == volume_name:
                volume_id = volume.get("id")
        return volume_id

    def get_driver_volume_id_from_list(self, volume_name):
        response = self.list_volume()
        if response.status_code != 200:
            return ""
        driver_volume_id = ""
        volumes = response.json().get("volumes")
        for volume in volumes:
            if volume.get("name") == volume_name:
                driver_volume_id = volume.get("driver_volume_id")
        return driver_volume_id
