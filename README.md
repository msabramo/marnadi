marnadi
=======

Yet another WSGI Web Framework, the simplest and fastest ever written.

Has no dependencies. Works both with **Python 2** and **Python 3**.

Features
--------
* Support both of functional and object-oriented programming styles
* Dynamic routes, e.g. "/path/{param}/"
* Headers, query, data, cookies descriptors
* Rich extending abilities

Hello World
-------

    from marnadi.wsgi import App
    from marnadi import Response
    
    application = App()
    
    
    @application.route('/')
    @Response.provider
    def hello():
        return "Hello World"
    
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        make_server('', 8000, application).serve_forever()


More Complex Example
-------

    import re
    from marnadi.wsgi import App
    from marnadi import Response, Route
    
    
    class MyResponse(Response):
    
        # HTTP GET request handler
        def get(self, foo, bar=None):
            return 'foo is {foo}, bar is {bar}'.format(foo=foo, bar=bar)
    
    routes=(
        Route('/{foo}'), (
            Route('/', MyResponse),
            Route('/{bar}/', MyResponse),
        )),
    )
    
    application = App(routes=routes)
    
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        make_server('', 8000, application).serve_forever()
