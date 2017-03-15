import datetime
import json
import time
import urllib
import requests
import logging

requests.packages.urllib3.disable_warnings()
logger = logging.getLogger(__name__)  # pylint: disable=C0103


class ShootingGroundClient(object):
    def __init__(self):
        self.address = None
        self.token = None
        self.api_token = ''
        self.api_timeout = None
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'User-Agent': 'tank'})
        if 'https' in requests.utils.getproxies():
            logger.info('Connecting via proxy %s' % requests.utils.getproxies()['https'])
            self.session.proxies = requests.utils.getproxies()
        else:
            logger.info('Proxy not set')

    def set_api_address(self, addr):
        self.address = addr.strip('/')

    def set_api_timeout(self, timeout):
        self.api_timeout = float(timeout)

    def set_api_token(self, api_token):
        self.api_token = api_token

    def _request(self, method, path, data=None):
        if not self.address:
            raise ValueError('Can\'t request unknown address')

        url = self.address + path
        logger.debug('Making request to: %s', url)
        req = requests.Request(method, url, data=data)
        prepared = self.session.prepare_request(req)
        resp = self.session.send(prepared, timeout=self.api_timeout)

        resp.raise_for_status()
        resp_data = resp.content.strip()
        logger.debug('Raw response: %s', resp_data)

        return resp.json()['data']

    def create_job(self, name):
        data = {
            'name': name,
        }

        logger.debug('Job create request: %s', data)

        response = self._request(
            'POST',
            '/jobs/',
            data=data,
        )
        return response['id']

    def send_job_record(self, job_id, data_item, stat_item, seconds_left):
        self._request(
            'POST',
            '/jobs/%s/records/' % job_id,
            data={
                'payload': json.dumps({
                    'data': data_item,
                    'stats': stat_item,
                }),
                'seconds': seconds_left,
                'type': 'yandex-tank',
            },
        )
