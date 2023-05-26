#!/bin/bash

config_file="/etc/eoti/local.conf"

# Verificar si el archivo de configuración existe
if [ -f "$config_file" ]; then
  # Leer la variable access_token del archivo de configuración
  access_token=$(sed -n 's/^access_token=\(.*\)/\1/p' "$config_file" | tr -d '\n')

  # Verificar si la variable access_token está presente
  if [ -n "$access_token" ]; then
    # Acción si el access_token está presente
    echo "connect to server: $access_token"
  else
    # Acción si el access_token no está presente
    echo "start ap"
  fi
else
    echo "start ap"
fi
