import unittest

from marnadi import Response, Route
from marnadi.wsgi import Request, App


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

        app = App(routes=routes)
        actual_result = b''.join(app(environ, start_response))
        self.assertEqual(expected_result, actual_result)

    def test_handler_as_function(self):
        routes = (
            Route('/', Response.provider(lambda: 'hello')),
        )
        environ = Request(dict(
            REQUEST_METHOD='GET',
            PATH_INFO='/',
        ))
        self.handler_parametrized_test_case(
            routes=routes,
            environ=environ,
            expected_result=b'hello',
            expected_headers=(
                ('Content-Type', 'text/plain; charset=utf-8'),
            ),
        )

    def test_handler_as_class(self):
        MyResponse = type('MyHandler', (Response, ), dict(
            get=lambda *args: 'hello'
        ))
        routes = (
            Route('/', MyResponse),
        )
        environ = Request(dict(
            REQUEST_METHOD='GET',
            PATH_INFO='/',
        ))
        self.handler_parametrized_test_case(
            routes=routes,
            environ=environ,
            expected_result=b'hello',
            expected_headers=(
                ('Content-Type', 'text/plain; charset=utf-8'),
            ),
        )
