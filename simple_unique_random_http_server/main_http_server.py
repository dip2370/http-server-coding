from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
from pathlib import Path

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils.random_number import RandomNumberGenerator
from utils.response_utils import construct_response
from utils.persistence_json_utils import load_used_numbers, save_used_numbers, define_persistence_file_path

# Constants and initialization
PERSISTENCE_FILE = define_persistence_file_path("used_numbers.json")
used_numbers = load_used_numbers(PERSISTENCE_FILE)
generator = RandomNumberGenerator()

class RandomNumberHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/random":
            try:
                query_params = parse_qs(parsed_path.query)
                is_float = query_params.get("type", ["int"])[0].lower() == "float"

                max_attempts = 100
                for _ in range(max_attempts):
                    number = generator.generate_random_number(is_float=is_float)
                    if number not in used_numbers:
                        used_numbers.add(number)
                        save_used_numbers(PERSISTENCE_FILE, used_numbers)
                        break
                else:
                    raise Exception("Could not generate a unique number after multiple attempts.")

                response = construct_response(data=number)
                self.send_response(200)
            except Exception as e:
                response = construct_response(error=str(e))
                self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            response = construct_response(error="Endpoint not found")
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())

def run(server_class=HTTPServer, handler_class=RandomNumberHandler, port=5000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}/random")
    httpd.serve_forever()

if __name__ == "__main__":
    run()