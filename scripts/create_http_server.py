import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

def configure_wifi(ssid, password):
    # Desconfigurar el punto de acceso
    subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'])
    subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'])

    # Configurar la conexión Wi-Fi
    subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password])

    print("Conexión Wi-Fi configurada exitosamente.")

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/start':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = json.loads(post_data)

            ssid = params.get('ssid')
            password = params.get('password')
            token = params.get('token')

            # Configurar la conexión Wi-Fi
            configure_wifi(ssid, password)

            
            response = send_auth_request(token)
            if response == 200:
                print('Token enviado correctamente. Actualizando la variable is_auth en el archivo de configuración...')
                update_config_file('is_auth', 'true')
            else:
                print(f'Error al enviar el token. Código de respuesta: {response}')

            response_data = {
                'status': 'success',
                'message': 'Script executed successfully',
                'output': response
            }
            response_json = json.dumps(response_data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_json.encode())
        else:
            self.send_error(404)


def send_auth_request(token):
    response = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', '-d', f'token={token}', 'http://eoti.com/api/auth'], capture_output=True, text=True)
    print(response.stdout.strip())
    return int(response.stdout.strip())


def update_config_file(variable_name, new_value):
    config_file = os.path.expanduser("~/.eoti/local.conf")
    variable_exists = False
    lines = []

    if os.path.isfile(config_file):
        with open(config_file, 'r') as file:
            for line in file:
                if line.startswith(f'{variable_name}='):
                    line = f'{variable_name}={new_value}\n'
                    variable_exists = True
                lines.append(line)

        if not variable_exists:
            lines.append(f'{variable_name}={new_value}\n')

        with open(config_file, 'w') as file:
            file.writelines(lines)

        print(f'Se ha modificado la variable {variable_name} en {config_file}')
    else:
        with open(config_file, 'w') as file:
            file.write(f'{variable_name}={new_value}\n')

        print(f'Se ha creado el archivo {config_file} y se ha definido la variable {variable_name} como {new_value}')


def run_server():
    host = '192.168.100.11'
    port = 8000
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Servidor iniciado en {}:{}'.format(host, port))
    httpd.serve_forever()


run_server()
