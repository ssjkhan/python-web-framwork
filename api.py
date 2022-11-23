import inspect
import os

from parse import parse
from webob import Request
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise

from response import Response
from middleware import Middleware

class API:
    def __init__(self, templates_dir="templates", static_dir = "static"):
        self.routes = {}
        
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir)))

        self.exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_app, root = static_dir)

        self.middleware = Middleware(self)


    def __call__(self, env, callback_):
        path_info = env["PATH_INFO"]

        if path_info.startswith("/static"):
            env["PATH_INFO"] = path_info[len("/static"):]
            return self.whitenoise(env, callback_)

        return self.middleware(env, callback_)

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    def wsgi_app(self, env, callback_):
        req = Request(env)
        resp = self.handle_request(req)

        return resp(env, callback_)

    def find_handler(self,req_path):
        for path, handler_data in self.routes.items():
            parse_res = parse(path, req_path)
            
            if parse_res is not None:
                return handler_data, parse_res.named
       
        return None, None

    def handle_request(self, req):
        resp = Response()

        handler_data, kwargs = self.find_handler(req.path)

        try:
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                
                if inspect.isclass(handler):
                    handler = getattr(handler(), req.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method not allowed", req.method)
                else:
                    if req.method.lower() not in allowed_methods:
                        raise AttributeError("Method not allowed", req.method)

                handler(req, resp, **kwargs)
            else:
                self.default_response(resp)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(req,resp,e)

        return resp

    def route(self, path, allowed_methods = None):
        assert path not in self.routes, f"Such a route already exists\n{path}\n"

        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def default_response(self, resp):
        resp.status_code = 404
        resp.text = "Not found"

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        
        return session

    def add_route(self, path, handler, allowed_methods=None):
        assert path not in self.routes, f"Such a route already exists\n{path}\n"

        if allowed_methods is None:
            allowed_methods = ["get", "post", "put", "delete", "options"]

        self.routes[path] = {'handler' : handler, 'allowed_methods' : allowed_methods }

    def template(self, template_name, context=None):
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context)


    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

