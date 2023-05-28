#!/bin/bash

# Función para manejar la petición POST
handle_post_request() {
    # Leer los datos JSON de la petición
    read -r content_length
    read -r -n "$content_length" json_data

    # Obtener los valores de ssid, password y token del JSON
    ssid=$(echo "$json_data" | jq -r '.ssid')
    password=$(echo "$json_data" | jq -r '.password')
    token=$(echo "$json_data" | jq -r '.token')

    # Hacer algo con los valores recibidos
    echo "SSID: $ssid"
    echo "Contraseña: $password"
    echo "Token: $token"

    # Responder a la petición con un mensaje de éxito
    response="HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\n{\"status\": \"OK\"}"
    echo -en "$response"
}

# Inicializar el servidor en el puerto 80
while true; do
    # Esperar a que llegue una petición
    request=$(nc -l -p 8000)
    echo ${request}
    # Extraer el método y la ruta de la petición
    method=$(echo "$request" | awk '{print $1}')
    path=$(echo "$request" | awk '{print $2}')
    echo ${method}
    echo ${path}
    # Verificar si la petición es POST y la ruta es "/"
    # echo ${method}
    echo ${path}
    if [[ "$method" == "POST" && "$path" == "/" ]]; then
        # Obtener el tamaño del cuerpo de la petición
        content_length=$(echo "$request" | grep -i "content-length:" | awk '{print $2}')

        # Manejar la petición POST
        handle_post_request

        # Salir del bucle para finalizar el servidor después de manejar una petición
        # break
    fi
done
