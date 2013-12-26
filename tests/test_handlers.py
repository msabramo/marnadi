import unittest

from marnadi import wsgi
from marnadi.handlers import Handler


class HandlerTestCase(unittest.TestCase):

    def handler_parametrized_test_case(
        self,
        routes,
        environ,
        expected_result,
        expected_status="200 OK",
        expected_headers=None,
        unexpected_headers=None,
    ):
        def start_response(status, headers):
            self.assertEqual(expected_status, status)
            for header in expected_headers or ():
                self.assertIn(header, headers)
            for header in unexpected_headers or ():
                self.assertNotIn(header, headers)

        app = wsgi.App(routes=routes)
        actual_result = ''.join(app(environ, start_response))
        self.assertEqual(expected_result, actual_result)

    def test_handler_as_function(self):
        routes = (
            ('/', Handler.decorator(lambda: 'hello')),
        )
        environ = wsgi.Environ(dict(
            request_method='GET',
            path_info='/',
        ))
        self.handler_parametrized_test_case(
            routes=routes,
            environ=environ,
            expected_result='hello',
            expected_headers=(
                ('Content-Length', '5'),
                ('Content-Type', 'text/plain; charset=utf-8'),
            ),
        )

    def test_handler_as_class(self):
        MyHadler = type('MyHandler', (Handler, ), dict(
            get=lambda *args: 'hello'
        ))
        routes = (
            ('/', MyHadler),
        )
        environ = wsgi.Environ(dict(
            request_method='GET',
            path_info='/',
        ))
        self.handler_parametrized_test_case(
            routes=routes,
            environ=environ,
            expected_result='hello',
            expected_headers=(
                ('Content-Length', '5'),
                ('Content-Type', 'text/plain; charset=utf-8'),
            ),
        )
