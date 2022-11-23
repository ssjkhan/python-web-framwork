from api import API
from middleware import Middleware

app = API()

@app.route("/home")
def home(req, resp):
    route = "HOME"
    resp.text = f"Hello from {route} page"

@app.route("/about")
def about(req, resp):
    route = "ABOUT"
    resp.text = f"Hello from {route} page"


@app.route("/hello/{name}")
def greeting(req, resp, name):
    resp.text = f"Hello {name}"


@app.route("/book")
class BooksResource:
    def get(self, req, resp):
        resp.text = "Books Page"
    
    def post(self, req, resp):
        resp.text = "Endpoint to create a book"

def handler(req, resp):
    resp.text = "sample"

app.add_route("/sample", handler)

@app.route("/exception")
def exception_throwing_handler(req,resp):
    raise AssertionError("This handler should not be used")

def custom_except_handler(req, resp, except_cls):
    resp.text = str(except_cls)

app.add_exception_handler(custom_except_handler)


# app.add_middleware()

class CustomMiddleware(Middleware):
    def process_req(self, req):
        print("Processing req\t", req.url)

    def process_resp(self, req,resp):
        print("Processing resp", req.url)

app.add_middleware(CustomMiddleware)

@app.route("/template")
def template_handler(req, resp):
    resp.html = app.template("index.html",
        context = {
            "name" : "Full stack practice",
            "title" : "Full stack dev"
        })

@app.route("/json")
def json_handler(req, resp):
    resp.json = {"name" : "data", "type" : "JSON"}

@app.route("/text")
def text_handler(req,resp):
    resp.text = "simple text"