import pytest
from api import API

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