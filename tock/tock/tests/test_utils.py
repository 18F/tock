import requests

from django.test import TestCase

from tock.settings import base, test
from tock.utils import check_status_code, get_free_port
from tock.mock_api_server import TestMockServer



class TestFloatAPIUtils(TestCase):

    def test_status_code_check(self):
        """Checks error is handled if response status code is not 200."""
        port = get_free_port()
        TestMockServer.run_server(port)
        endpoint = 'fish'
        r = requests.get(
            url='{}:{}/{}'.format(test.FLOAT_API_URL_BASE, port, endpoint)
        )
        result = check_status_code(r)
        self.assertIn('Status code: {}'.format(r.status_code), str(result))
