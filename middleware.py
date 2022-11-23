from webob import Request

class Middleware:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, env, callback_):
        req = Request(env)
        resp = self.app.handle_request(req)
        return resp(env, callback_)


    def add(self, middleware_cls):
        self.app =  middleware_cls(self.app)

    def process_req(self, req):
        pass
    def process_resp(self, req, resp):
        pass

    def handle_request(self, req):
        self.process_req(req)
        
        response = self.app.handle_request(req)
        
        self.process_resp(req,response)

        return response