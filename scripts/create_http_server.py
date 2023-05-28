from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        if self.path == '/start':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = json.loads(post_data)

            ssid = params.get('ssid')
            password = params.get('password')
            token = params.get('token')

            # Ejecutar el script de Linux
            resultado = subprocess.run(['bash', 'connect_to_wifi.sh', ssid, password, token], capture_output=True, text=True)
            
            # Crear la respuesta en JSON
            response_data = {
                'status': 'success',
                'message': 'Script executed successfully',
                'output': resultado.stdout
            }
            response_json = json.dumps(response_data)
            print(resultado)
            # Enviar la respuesta al cliente
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_json.encode())
        else:
            self.send_error(404)

def run_server():
    host = '192.168.100.7'
    port = 8000
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Servidor iniciado en {}:{}'.format(host, port))
    httpd.serve_forever()

run_server()
