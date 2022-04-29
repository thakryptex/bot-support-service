import ujson as json


class JsonParamsToRequest(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.method in ['POST', 'PUT', 'DELETE']:
            try:
                body = request.body.decode('utf-8')
                json_params = json.loads(body)
            except:
                json_params = {}

            request.JSON = json_params

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
