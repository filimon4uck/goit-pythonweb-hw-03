import urllib.parse
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import json
from datetime import datetime


from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
jinja = Environment(loader=FileSystemLoader("frontend/templates"))
print("after jinja")


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        pages_path = "frontend/pages/"
        match route.path:
            case "/":
                self.send_html(f"{pages_path}index.html")
            case "/message":
                self.send_html(f"{pages_path}message.html")
            case "/read":
                self.render_template("read.jinja")
            case _:
                file = search_file(BASE_DIR, route.path[1:])
                if file:
                    print(f"{route.path=}")
                    self.send_static(file)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data_dict = {
            key: value
            for key, value in [el.split("=") for el in data_parse.split("&")]
            if key and value
        }
        if data_dict:
            with open("storage/data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                data.update({time: data_dict})
            with open("storage/data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status=200):
        print(filename)
        self.send_response(status)
        mime_type = mimetypes.guess_type(filename)
        self.send_header("Content-type", mime_type if mime_type else "text/plain")
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def render_template(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        with open("storage/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            template = jinja.get_template(filename)
            content = template.render(messages=data)
            self.wfile.write(content.encode())


def run(server_class=HTTPServer, handler_class=MyHandler):

    server_address = ("", 3000)
    httpd = server_class(server_address, handler_class)
    print("Server started on port - 3000")
    httpd.serve_forever()


def search_file(path, file):
    for element in Path(path).iterdir():
        if element.is_dir():
            result = search_file(element, file)
            if result:
                return result
        if element.is_file() and element.name == file:
            return element
    return None



