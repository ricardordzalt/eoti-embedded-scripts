#!/bin/bash

# Ejecutar el primer script y capturar su resultado
source ./check_startup.sh
# Verificar el resultado y ejecutar el siguiente script
if [ "$has_token" -eq 0 ]; then
  # source ./start_access_point.sh
  source ./create_http_server.sh
  if [ "$is_auth" -eq 1 ]; then
    echo "Bien!"
  fi
else
  source ./connect_to_server.sh
fi
