import functools
import logging

from marnadi import errors, descriptors, Header


class HandlerProcessor(type):

    logger = logging.getLogger('marnadi')

    def __new__(mcs, name, bases, attributes):
        cls = super(HandlerProcessor, mcs).__new__(mcs, name, bases, attributes)
        for attr_name, attr_value in attributes.iteritems():
            cls.set_descriptor_name(attr_value, attr_name)
        return cls

    def __setattr__(cls, attr_name, attr_value):
        super(HandlerProcessor, cls).__setattr__(attr_name, attr_value)
        cls.set_descriptor_name(attr_value, attr_name)

    def __call__(cls, *args, **kwargs):
        if cls.func is not None:
            return cls.func(*args, **kwargs)
        return super(HandlerProcessor, cls).__call__(*args, **kwargs)

    def decorator(cls, func):
        method = staticmethod(func)
        attributes = dict(func=method)
        for supported_method in cls.SUPPORTED_HTTP_METHODS:
            supported_method = supported_method.lower()
            if getattr(cls, supported_method, NotImplemented) is NotImplemented:
                attributes[supported_method] = method
        return functools.update_wrapper(
            type('', (cls, ), attributes),
            func, updated=(),
        )

    def handle(cls, environ, args=(), kwargs=None):
        try:
            handler = super(HandlerProcessor, cls).__call__(environ)
            result = handler(*args, **kwargs or {})
            chunks, first_chunk, chunked = (), '', False
            try:
                assert not isinstance(result, basestring)
                chunks = iter(result)
            except (AssertionError, TypeError):
                first_chunk = unicode(result or '').encode('utf-8')
            else:
                try:
                    first_chunk = unicode(chunks.next()).encode('utf-8')
                except StopIteration:
                    # only StopIteration exception alone should be caught
                    # at this place
                    pass
            if not handler.headers.setdefault('Content-Length'):
                try:
                    assert not (chunks and len(result) > 1)
                    handler.headers['Content-Length'] = len(first_chunk)
                except (TypeError, AssertionError):
                    handler.headers['Transfer-Encoding'] = 'chunked'
                    chunked = True
            yield handler.status
            for header, value in handler.headers.flush():
                yield header, str(value)
            yield  # separator between headers and body
            if first_chunk:
                yield cls.make_chunk(first_chunk, chunked)
            for next_chunk in chunks:
                next_chunk = unicode(next_chunk).encode('utf-8')
                if next_chunk:
                    yield cls.make_chunk(next_chunk, chunked)
            yield cls.make_chunk('', chunked)  # end of stream
        except errors.HttpError:
            raise
        except Exception as error:
            cls.handle_exception(error)

    def handle_exception(cls, error):
        cls.logger.exception(error)
        raise errors.HttpError(exception=error)

    @staticmethod
    def make_chunk(chunk, chunked=False):
        if chunked:
            return '%X\r\n%s\r\n' % (len(chunk), chunk)
        return chunk

    @staticmethod
    def set_descriptor_name(descriptor, attr_name):
        if isinstance(descriptor, descriptors.Descriptor):
            descriptor.attr_name = attr_name


class Handler(object):

    __metaclass__ = HandlerProcessor

    SUPPORTED_HTTP_METHODS = (
        'OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE',
    )

    status = '200 OK'

    headers = descriptors.Headers(
        ('Content-Type', Header('text/plain', charset='utf-8')),
    )

    cookies = descriptors.Cookies()

    query = descriptors.Query()

    data = descriptors.Data(
        ('application/json', 'marnadi.mime.application.json.Decoder'),
        ('application/x-www-form-urlencoded',
            'marnadi.mime.application.x_www_form_urlencoded.Decoder'),
    )

    func = None  # function decorated by this class

    def __init__(self, environ):
        self.environ = environ

    def __call__(self, *args, **kwargs):
        request_method = self.environ.request_method
        if request_method not in self.SUPPORTED_HTTP_METHODS:
            raise errors.HttpError(
                '501 Not Implemented',
                headers=(('Allow', ', '.join(self.allowed_http_methods)), )
            )
        callback = getattr(self, request_method.lower(), NotImplemented)
        if callback is NotImplemented:
            raise errors.HttpError(
                '405 Method Not Allowed',
                headers=(('Allow', ', '.join(self.allowed_http_methods)), )
            )
        return callback(*args, **kwargs)

    @property
    def allowed_http_methods(self):
        for method in self.SUPPORTED_HTTP_METHODS:
            if getattr(self, method.lower(), NotImplemented) is NotImplemented:
                continue
            yield method

    def options(self, *args, **kwargs):
        self.headers['Allow'] = ', '.join(self.allowed_http_methods)

    get = NotImplemented

    head = NotImplemented

    post = NotImplemented

    put = NotImplemented

    patch = NotImplemented

    delete = NotImplemented
