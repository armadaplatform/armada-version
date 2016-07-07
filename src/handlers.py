import uuid
import logging
from urllib.parse import urlencode

from armada import hermes
from tornado.gen import Task
from tornado.ioloop import IOLoop
from tornado.escape import json_decode
from tornado.web import RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient, HTTPError as HTTPClientError, HTTPRequest

from utils import status, StrictVerboseVersion


http_client = AsyncHTTPClient()
config = hermes.get_config('config.json')
logging.basicConfig(format='%(asctime)-15s %(message)s')


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

    @staticmethod
    async def make_request(url, method='GET', body=None, timeout=None):
        request = HTTPRequest(url, method, body=body, request_timeout=timeout)
        response = await Task(http_client.fetch, request)
        if response.error:
            raise response.error
        return response

    async def _get_latest_version(self):
        try:
            response = await self.make_request('http://dockyard.armada.sh/v2/armada/tags/list', timeout=3)
        except HTTPClientError:
            logging.exception('There was a problem with connecting to external service.')
            raise HTTPError(500, reason="Due to failure of third party services, "
                                        "we weren't able to handle your request.")
        tags = json_decode(response.body)['tags']
        try:
            return max(self._get_valid_versions(tags))
        except ValueError:
            logging.error("Couldn't find any valid version number in armada's dockyard.")
            raise HTTPError(500, reason="We could't find any valid version candidate.")

    async def _collect_data(self, client_version, ip_address):
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
            await self.make_request('https://www.google-analytics.com/collect', method='POST', body=body, timeout=5)
        except HTTPClientError:
            logging.exception('An error occurred while trying to send Google Analytics.')

    @staticmethod
    def _get_valid_versions(tags):
        for tag in tags:
            try:
                yield StrictVerboseVersion(tag)
            except ValueError:
                pass

    def _validate_client_version(self):
        client_version = self.get_argument('version')
        if not client_version:
            raise HTTPError(400, reason='Missing argument version.')
        try:
            return StrictVerboseVersion(client_version)
        except ValueError:
            raise HTTPError(400, reason='Invalid version number.')
