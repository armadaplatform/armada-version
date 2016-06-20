import uuid
import logging
from urllib.parse import urlencode
from distutils.version import StrictVersion

from armada import hermes
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPError

from utils import status


http_client = AsyncHTTPClient()
config = hermes.get_config('config.json')


class IndexHandler(RequestHandler):
    def get(self):
        self.write(status())


class VersionCheckHandler(RequestHandler):
    async def get(self):
        client_version = self._validate_client_version()
        # send version to GA, fire and forget
        IOLoop.current().spawn_callback(self._collect_data, client_version, self.request.remote_ip)
        latest_version = await self._get_latest_version()
        data = {
            'latest_version': str(latest_version),
            'is_newer': latest_version > client_version
        }
        self.write(data)

    async def _get_latest_version(self):
        try:
            response = await http_client.fetch('http://192.168.3.158:5001/v2/armada/tags/list')
        except HTTPError:
            logging.exception('There was a problem with connecting to external service.')
            raise HTTPError(code=500, message="Due to failure of third party services, "
                                              "we weren't able to handle your request.")
        tags = json_decode(response.body)['tags']
        try:
            return max(self._get_valid_versions(tags))
        except ValueError:
            logging.error("Couldn't find any valid version number in armada's dockyard.")
            raise HTTPError(code=500, message="We could't find any valid version candidate.")

    @staticmethod
    async def _collect_data(client_version, ip_address):
        data = {
            'v': 1,
            't': 'screenview',
            'tid': config['tid'],
            'cid': str(uuid.uuid4()),
            'an': 'armada-version',
            'cd': 'version-check',
            'av': str(client_version),
            'uip': ip_address  # uip is anonymized by default
        }

        body = urlencode(data)
        try:
            await http_client.fetch('https://www.google-analytics.com/collect', method='POST', body=body)
        except HTTPError:
            logging.exception('An error occurred while trying to send Google Analytics.')

    @staticmethod
    def _get_valid_versions(tags):
        for tag in tags:
            try:
                yield StrictVersion(tag)
            except ValueError:
                pass

    def _validate_client_version(self):
        client_version = self.get_argument('version')
        if not client_version:
            raise HTTPError(code=400, message='Missing argument version.')
        try:
            return StrictVersion(client_version)
        except ValueError:
            raise HTTPError(code=400, message='Invalid version number.')
