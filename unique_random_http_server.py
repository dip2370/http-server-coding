from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from unique_random_number_generator import UniqueRandomNumberGenerator

# Define constants
MIN_NUM = 10
MAX_NUM = 1000
PERSISTENCE_FILE = Path("used_numbers.json")

# Initialize the random number generator
generator = UniqueRandomNumberGenerator(MIN_NUM, MAX_NUM, PERSISTENCE_FILE)

class RandomNumberHandler(BaseHTTPRequestHandler):
    #HTTP handler for serving unique random numbers.

    def do_GET(self):
        
        #Handles GET requests to the /random endpoint.

        if self.path == "/random":
            try:
                number = generator.generate()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"number": number}).encode())
            except Exception as e:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

def run(server_class=HTTPServer, handler_class=RandomNumberHandler, port=5000):

    #Start the HTTP server.

    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}/random")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
