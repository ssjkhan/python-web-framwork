from webob import Request, Response
from parse import parse
import inspect
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from requests import Session as RequestsSession
import os
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise


class API:
    def __init__(self, templates_dir="templates", static_dir = "static"):
        self.routes = {}
        
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir)))

        self.exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_app, root = static_dir)

    def __call__(self, env, callback_):
        return self.whitenoise(env, callback_)

    def wsgi_app(self, env, callback_):
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

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), req.method.lower(), None)
                    if handler is None:
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

    def route(self, path):
        assert path not in self.routes, f"Such a route already exists\n{path}\n"

        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def default_response(self, resp):
        resp.status_code = 404
        resp.text = "Not found"

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        
        return session

    def add_route(self, path, handler):
        assert path not in self.routes, f"Such a route already exists\n{path}\n"

        self.routes[path] = handler

    def template(self, template_name, context=None):
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context)


    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler