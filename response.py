import json

from webob import Response as WebObResp

class Response:
    def __init__(self):
        self.json = None
        self.html = None
        self.text = None
        self.content_type = None
        self.body = b''
        self.status_code = 200

    def __call__(self, env, callback_):
        self.set_body_and_content_type()

        resp = WebObResp(
            body =self.body,
            content_type=self.content_type,
            status=self.status_code
        )

        return resp(env, callback_)

    def set_body_and_content_type(self):
        if self.json is not None:
            self.body = json.dumps(self.json).encode("UTF-8")
            self.content_type = "application/json"

        if self.html is not None:
            self.body = self.html.encode()
            self.content_type = "text/html"
        
        if self.text is not None:
            self.body = self.text
            self.content_type = "text/plain"