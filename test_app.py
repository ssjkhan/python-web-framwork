import pytest
from api import API
from middleware import Middleware
# helpers

FILE_DIR = "css"
FILE_NAME = "main.css"
FILE_CONTENTS = "body {background-color: red}"

def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)

    return asset

# tests

def test_basic_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "YOLO"
    
    with pytest.raises(AssertionError):
        @api.route("/home")
        def home_2(req, resp):
            resp.text = "YOLO"

def test_client_send_request(api,client):
    resp_txt = "cool text"

    @api.route("/hey")
    def cool(req, resp):
        resp.text = resp_txt

    assert client.get("http://testserver/hey").text == resp_txt

def test_route_paramters(api,client):
    @api.route("/{name}")
    def hello(req,resp,name):
        resp.text = f"{name}"

    assert client.get("http://testserver/matthew").text == "matthew"
    assert client.get("http://testserver/saad").text == "saad"

def test_default_resp(client):
    resp = client.get("http://testserver/doesnotexist")
    assert resp.status_code == 404
    assert resp.text == "Not found"


def test_handler_class_get(api,client):
    resp_text = "get request"

    @api.route("/book")
    class BookResource:
        def get (self, req, resp):
            resp.text = resp_text

    assert client.get("http://testserver/book").text == resp_text

def test_handler_class_post(api,client):
    resp_text = "post request"

    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = resp_text

    assert client.post("http://testserver/book").text == resp_text

def test_handler_class_method_invalid(api, client):
    @api.route("/book")
    class BookResource:
        def post(self, req, resp):
            resp.text = "yolo"

    with pytest.raises(AttributeError):
        client.get("http://testserver/book")

def test_alternative_route(api, client):
    resp_text = "alternate route definition"

    def home(req, resp):
        resp.text = resp_text
    
    api.add_route("/alternative", home)

    assert client.get("http://testserver/alternative")


def test_template(api,client):
    @api.route("/html")
    def html_handler(req,resp):
        resp.body = api.template(
            "index.html",
            context= {
                "title" : "my title",
                "name" : "my name"}).encode()
            
    response = client.get("http://testserver/html")
    
    assert "text/html" in response.headers["Content-Type"]
    assert "my title" in response.text
    assert "my name" in response.text


def test_exception_handler(api,client):
    def on_exception(req, resp, except_):
        resp.text="Attribute Error Happened"
    
    api.add_exception_handler(on_exception)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get("http://testserver")

    assert response.text == "Attribute Error Happened"

def text_static_404(client):
    assert client.get(f"http://textserver/static/main.css").status_code == 404


def test_static_assets_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_static(static_dir)
    api = API(static_dir=str(static_dir))
    client = api.test_session()

    response = client.get(f"http://testserver/static/{FILE_DIR}/{FILE_NAME}")

    assert response.status_code == 200
    assert response.text == FILE_CONTENTS

def test_middleware_method_call(api,client):
    proc_req_called = False
    proc_resp_called = False

    class CallMiddlewareMethods(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_req(self,req):
            nonlocal proc_req_called
            proc_req_called = True

        def process_resp(self, req, resp):
            nonlocal proc_resp_called
            proc_resp_called = True

    api.add_middleware(CallMiddlewareMethods)

    @api.route("/")
    def index(req,resp):
        resp.text = "YOLO"

    client.get("Http://testserver/")

    assert proc_req_called is True
    assert proc_resp_called is True

def test_allowed_methods_for_function_based_handlers(api,client):
    @api.route("/home", allowed_methods = "post")

    def home(req, resp):
        resp.text = "hello"

    with pytest.raises(AttributeError):
        client.get("http://testserver/home")

    assert client.post("http://testserver/home").text == "hello"

def test_response_json(api, client):
    @api.route("/json")
    def json_handler(req,resp):
        resp.json = {"name" : "full stack exercise"}

    response = client.get("http://testserver/json")
    json_body = response.json()

    assert response.headers["Content-Type"] == "application/json"
    assert json_body["name"] == "full stack exercise"

def test_response_html(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.html = api.template("index.html", context = {
            "title" : "a title",
            "name" : "a name"})

    response = client.get("http://testserver/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "a title" in response.text
    assert "a name" in  response.text

def test_response_text(api, client):
    @api.route("/body")
    def text_handler(req, resp):
        resp.body = b"i byte u"
        resp.content_type = "text/plain"

    response = client.get("http://testserver/body")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == "i byte u"


    