from webob import Request, Response
from parse import parse

class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, env, callback_):
        req = Request(env)

        resp = self.handle_request(req)

        return resp(env, callback_)

    def find_handler(self,req_path):
        for path, handler in self.routes.items():
            parse_res = parse(path, req_path)
            if parse_res is not None:
                return handler, parse_res.named
        return None, None

    def handle_request(self, req):
        resp = Response()

        handler, kwargs = self.find_handler(req.path)
        
        if handler is not None:
            handler(req, resp, **kwargs)
        else:
            self.default_response(resp)

        return resp

    def route(self, path):
        if path in self.routes :
            raise AssertionError("Such a route already exists")

        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def default_response(self, resp):
        resp.status_code = 404
        resp.text = "Not found"