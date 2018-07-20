import requests
from common.logging import Logging
from common import settings

logger = Logging.get_logger()


class AlaudaRequest(object):
    def __init__(self):
        self.endpoint = settings.API_URL
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.namespace = settings.NAMESPACE
        self.username = settings.USERNAME
        self.region_name = settings.REGION_NAME
        self.password = settings.PASSWORD
        self.registry_name = settings.REGISTRY_NAME
        if self.username:
            self.auth = ("{}/{}".format(self.namespace, self.username), self.password)
        else:
            self.auth = (self.namespace, self.password)

    def send(self, method, path, auth=None, data={}, headers={}, params={}, version='v1'):
        url = self._get_url(path, version)

        if headers:
            headers = dict(self.headers.items() + headers.items())
        else:
            headers = self.headers

        args = {'headers': headers}

        args['auth'] = auth or self.auth

        if params:
            args['params'] = params

        if data is not None:
            if headers['Content-Type'] == 'application/json':
                args['json'] = data
            else:
                args['data'] = data

        files = data and data.pop('files', None) or None
        if files:
            args['files'] = files
        logger.info('Requesting url={}, method={}, args={}'.format(url, method, args))
        response = requests.request(method, url, **args)
        if response.status_code < 200 or response.status_code > 300:
            logger.info("response code={}, text={}".format(response.status_code, response.json()))
        else:
            logger.info("response code={}".format(response.status_code))

        return response

    def _get_url(self, path, version):
        return '{}/{}/{}'.format(self.endpoint, version, path)
