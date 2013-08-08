import importlib
json = importlib.import_module('json')  # workaround for importing global json

from marnadi import mime


class Decoder(mime.Decoder):

    def __call__(self, data, headers, content_params):
        return json.loads(data)