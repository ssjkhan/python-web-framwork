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