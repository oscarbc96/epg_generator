import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from epg_generator import EPGGenerator
from conf import HOST_NAME, PORT_NUMBER, EPG_FILE


class EPGServer(BaseHTTPRequestHandler):
    def do_GET(self):
        with open(EPG_FILE) as fh:
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.end_headers()
            self.wfile.write(fh.read().encode())


if __name__ == "__main__":
    # EPGGenerator().run()

    server_class = HTTPServer

    httpd = server_class((HOST_NAME, PORT_NUMBER), EPGServer)

    print(time.asctime(), f"Server Starts - {HOST_NAME}:{PORT_NUMBER}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()

    print(time.asctime(), f"Server Stops - {HOST_NAME}:{PORT_NUMBER}")
