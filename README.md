marnadi
=======

Yet another WSGI Web Server, the simplest and fastest ever written

Hello World
-------
    from marnadi import handlers, wsgi


    @handlers.handler
    def hello():
        return "Hello World"

    routes=(
        ('/', hello),
    )
    application = wsgi.App(routes=routes)

    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        make_server('', 8000, application).serve_forever()

More Complex Example
-------

    import json
    import re
    from marnadi import handlers, wsgi


    class JsonHandler(handlers.Handler):

        SUPPORTED_HTTP_METHODS = ('OPTIONS', 'GET')

        headers = descriptors.Headers(
            ('Content-Type', 'application/json; charset=utf-8'),
        )

        def __call__(self, *args, **kwargs):
            result = super(JsonHandler, self).__call__(*args, **kwargs)
            return json.dumps(result)

        def get(self, receiver, sender=None):
            return {'Hello':  receiver, 'from': sender}


    @handlers.handler(JsonHandler)
    def foo(bar):
        return {'foo': bar}

    routes=(
        ('/', handlers.Handler),  # HTTP 405 Method Not Allowed
        (re.compile(r'/foo/(?P<bar>\w+')$'), foo),
        (re.compile(r'/hello/(?P<receiver>\w+')/?, (
            ('', JsonHandler),
            (re.compile(r'/from/(?P<sender>\w+)$'), JsonHandler),
        )),
    )

    application = wsgi.App(routes=routes)

    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        make_server('', 8000, application).serve_forever()