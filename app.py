from api import API

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

@app.route("/template")
def template_handler(req,resp):
    resp.body = app.template(
        "index.html", context = {
            "name" : "Python Full Stack Practice",
            "title" : "My Python Framework"}).encode()

@app.route("/exception")
def exception_throwing_handler(req,resp):
    raise AssertionError("This handler should not be used")

def custom_except_handler(req, resp, except_cls):
    resp.text = str(except_cls)

app.add_exception_handler(custom_except_handler)
