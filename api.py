from webob import Request, Response

class API:
    def __init__(self):
        self.routes = {
            "/home" : None,
            "/about" : None
        }

    def __call__(self, env, callback_):
        req = Request(env)

        resp = self.handle_request(req)

        return resp(env, callback_)

    def find_handler(self,req_path):
        for path, handler in self.routes.items():
            if path == req_path:
                return handler

    def handle_request(self, req):
        resp = Response()

        handler = self.find_handler(req.path)
        
        if handler is not None:
            handler(req, resp)
        else:
            self.default_response(resp)

        return resp

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def default_response(self, resp):
        resp.status_code = 404
        resp.text = "Not found"