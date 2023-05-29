from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import os

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        if self.path == '/start':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = json.loads(post_data)

            ssid = params.get('ssid')
            password = params.get('password')
            token = params.get('token')

            # Ejecutar la petición POST al API de autenticación
            response = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', '-d', f'token={token}', 'http://eoti.com/api/auth'], capture_output=True, text=True)
            print(response)
            if response.stdout.strip() == '200':
                print('Token enviado correctamente. Actualizando la variable is_auth en el archivo de configuración...')

                # config_file = "$HOME/.eoti/local.conf"
                config_file = os.path.expanduser("~/.eoti/local.conf")
                variable_name = "is_auth"
                new_value = "true"
                # Verificar si el archivo de configuración existe
                if os.path.isfile(config_file):
                    lines = []
                    variable_exists = False

                    # Leer el archivo y buscar la variable
                    with open(config_file, "r") as file:
                        for line in file:
                            if line.startswith(variable_name + "="):
                                line = f"{variable_name}={new_value}\n"
                                variable_exists = True
                            lines.append(line)
                        
                        # Si la variable no existe, agregarla al final del archivo
                        if not variable_exists:
                            lines.append(f"{variable_name}={new_value}\n")

                    # Escribir las líneas modificadas en el archivo
                    with open(config_file, "w") as file:
                        file.writelines(lines)
                    
                    print(f"Se ha modificado la variable {variable_name} en {config_file}")
                else:
                    # Si el archivo no existe, crearlo y escribir la variable
                    with open(config_file, "w") as file:
                        file.write(f"{variable_name}={new_value}\n")
                    
                    print(f"Se ha creado el archivo {config_file} y se ha definido la variable {variable_name} como {new_value}")

                # config_file = "$HOME/.eoti/local.conf"
                # variable_name = "is_auth"
                # new_value = "true"

                # # Leer el contenido del archivo
                # with open(config_file, 'r') as file:
                #     lines = file.readlines()

                # # Buscar la línea que contiene la variable
                # for i, line in enumerate(lines):
                #     if line.startswith(variable_name + '='):
                #         lines[i] = variable_name + '=' + new_value + '\n'
                #         break
                # else:
                #     # La línea no existe, agregarla al final del archivo
                #     lines.append(variable_name + '=' + new_value + '\n')

                # # Escribir el contenido modificado en el archivo
                # with open(config_file, 'w') as file:
                #     file.writelines(lines)
            else:
                print(f'Error al enviar el token. Código de respuesta: {response.stdout.strip()}')
            
            # Crear la respuesta en JSON
            response_data = {
                'status': 'success',
                'message': 'Script executed successfully',
                'output': response.stdout.strip()
            }
            response_json = json.dumps(response_data)
            
            # Enviar la respuesta al cliente
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_json.encode())
        else:
            self.send_error(404)

def run_server():
    host = '192.168.100.11'
    port = 8000
    server_address = (host, port)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Servidor iniciado en {}:{}'.format(host, port))
    httpd.serve_forever()

run_server()
