import urlparse

from marnadi.descriptors import Descriptor


class Query(Descriptor):

    def get_value(self, handler):
        return self.decode(handler.environ)

    @staticmethod
    def decode(environ):
        try:
            return urlparse.parse_qsl(
                environ.query_string,
                keep_blank_values=True,
            )
        except AttributeError:  # query_string not in environ
            return ()