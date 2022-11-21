from webob import Request, Response

class API:
    def __call__(self, env, callback_):
        req = Request(env)

        resp = self.handle_request(req)

        return resp(env, callback_)

    def handle_request(self, req):
        user_agent = req.environ.get("HTTP_USER_AGENT", "No User Agent Found")

        resp = Response()
        resp.text = f"user agent: {user_agent}"

        return resp

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper