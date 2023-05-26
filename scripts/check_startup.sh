#!/bin/bash

config_file="/etc/eoti/local.conf"

# Verificar si el archivo de configuración existe
if [ -f "$config_file" ]; then
  # Leer la variable access_token del archivo de configuración
  access_token=$(sed -n 's/^access_token=\(.*\)/\1/p' "$config_file" | tr -d '\n')

  # Verificar si la variable access_token está presente
  if [ -n "$access_token" ]; then
    # Acción si el access_token está presente
    has_token="1"
  else
    # Acción si el access_token no está presente
    has_token="0"
  fi
else
    has_token="0"
fi
