#!/usr/local/bin/env python3
import http.server, os, mimetypes, urllib.request, string, server_config

class handler(http.server.BaseHTTPRequestHandler):

    def return_404(self):
            with open(os.path.join(server_config.template_dir, "404.html"), "rb") as notfounded:
                result_404 = notfounded.read()
                self.send_response(404, "Not Found")
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(result_404)

    def do_GET(self):
        request_path = self.path[1:]
        if request_path == "":
            request_path = server_config.toppage
        request_path = urllib.request.url2pathname(request_path)
        if not os.path.exists(request_path):
            self.return_404()

        elif os.path.exists(request_path) and os.path.isfile(request_path):
            with open(request_path, "rb") as f:
                res_bytes = f.read()
                self.send_response(200, "OK")
                self.send_header("Content-Type", mimetypes.guess_type(request_path, False)[0])
                self.send_header("Access-Control-Allow-Origin", "*");
                self.send_header("Last-Modified", os.stat(request_path).st_mtime)
                self.send_header("Content-length", len(res_bytes))
                self.send_header("Date", self.date_time_string())
                self.send_header("Server", self.server_version)
                self.end_headers()
                self.wfile.write(res_bytes)
        elif os.path.exists(request_path) and os.path.isdir(request_path):
            self.open_dir()

    def do_HEAD(self):
        request_path = self.path[1:]
        self.send_header("Date", self.date_time_string())
        self.send_header("Server", self.server_version)
        if os.path.exists(request_path):
            s = os.stat(request_path)
            self.send_header("Content-length", s[6])
            self.send_header("Last-Modified", s.st_mtime)
            self.end_headers()
        elif request_path == "":
            if os.path.exists("index.html"):
                request_path = "index.html"
                s = os.stat(request_path)
                self.send_header("Content-Type", mimetypes.guess_type(request_path, False)[0])
                self.send_header("Content-length", s[6])
                self.send_header("Last-Modified", self.date_time_string(s.st_mtime))
                self.end_headers()
            else: 
                self.end_headers()

    def open_dir(self):
        r_path = urllib.request.url2pathname(self.path[1:])
        dir_list = os.listdir(r_path)
        with open(os.path.join(server_config.template_dir, "dir_page.html"), "r") as m:
            links = ["<li><a href=" + os.path.join(self.path, v) + ">" + v + "</a></li>" for v in dir_list]
            return_str = "<ul>\n" + "\n".join(links) + "</ul>"
            template = string.Template(m.read())
            result_str = template.safe_substitute({"list": return_str})
            dir_res_bytes = result_str.encode()
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*");
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(dir_res_bytes)


server_address = (server_config.domain, server_config.port)
httpd = http.server.HTTPServer(server_address, handler);
print("server listening at " + server_address[0] + " " + str(server_address[1]))
httpd.serve_forever()
