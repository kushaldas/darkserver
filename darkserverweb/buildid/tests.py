from django.test import TestCase
import json
from xmlrpclib import ServerProxy
from mock import Mock, patch

import httplib
from xmlrpclib import getparser, ProtocolError

class DjangoTestClientTransport(object):
    client = None

    def __init__(self, client):
        self.client = client

    def getparser(self):
        return getparser()

    def request(self, host, handler, request_body, verbose = False):
        parser, unmarshaller = self.getparser()
        response = self.client.post(handler, request_body, 'text/xml')
        if response.status_code != 200:
            raise ProtocolError(
              '%s%s' % (host, handler),
              response.status_code,
              httplib.responses.get(response.status_code, ''),
              dict(response.items()),
            )
        parser.feed(response.content)
        return unmarshaller.close()


class BuildidViewTest(TestCase):
    fixtures = ['buildid_data.json']

    def get_server_proxy(self):
        return ServerProxy(
          'http://testserver/xmlrpc/',
          transport = DjangoTestClientTransport(self.client),
        )

    def test_index(self):
        """
        Tests index view
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_serverversion(self):
        """
        Test the server version call
        """
        resp = self.client.get('/serverversion')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['server-version'],'0.5')

    def test_buildids(self):
        """
        Tests index view
        """
        resp = self.client.get('/buildids/868357887701f51d867eacd0da6e5af6d8c70ce2')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data[0]['rpm'], 'apr-1.4.5-1.fc16.x86_64')

    def test_rpm2buildids(self):
        """
        Tests index view
        """
        resp = self.client.get('/rpm2buildids/apr-1.4.5-1.fc16.x86_64')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data[0]['elf'], '/usr/lib64/libapr-1.so.0.4.5')

    @patch('koji.pathinfo.rpm')
    @patch('koji.ClientSession')
    def test_package(self,mock_c, mock_2):
        """
        Tests index view
        """
        m = mock_c.return_value
        m.search.return_value = [{'id':1},]
        m.getRPM.return_value = {'build_id':'32123'}
        m.getBuild.return_value = {'name':'foobar','version':'1.0','release':'1.fc16'}
        mock_2.return_value = 'file.rpm'
        resp = self.client.get('/package/apr-1.4.5-1.fc16.x86_64')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        url = data['url']
        self.assertEqual(url,'http://koji.fedoraproject.org/packages/foobar/1.0/1.fc16/file.rpm')

    def test_xmlrpcfail(self):
        """
        Tests xmlrpcview
        """
        resp = self.client.get('/xmlrpc/')
        self.assertEqual(resp.status_code, 200)

    def test_xmlrpc_multiply(self):
        """
        Tests xmlrpcview multiply call
        """
        s = self.get_server_proxy()
        res = s.multiply(2,3)
        self.assertEqual(res, 6)

