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
