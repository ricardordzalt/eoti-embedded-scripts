#!/bin/bash

# Ruta al archivo de configuración
CONFIG_FILE="$HOME/.eoti/local.conf"

# Ruta al programa en Python
PYTHON_SCRIPT="create_http_server.py"

# Variable a monitorear
VARIABLE="is_auth"

# Obtener el valor inicial de la variable del archivo de configuración
# initial_value=$(grep -Po "(?<=^$VARIABLE=).*" "$CONFIG_FILE")
initial_value=$(grep -Eo "^$VARIABLE=.*" "$CONFIG_FILE" | awk -F '=' '{print $2}')



# Función para ejecutar el programa en Python
run_python_script() {
    python3 "$PYTHON_SCRIPT"
}

# Función para comprobar si la variable ha cambiado en el archivo de configuración
check_variable_changes() {
    # current_value=$(grep -Po "(?<=^$VARIABLE=).*" "$CONFIG_FILE")
    current_value=$(grep -Eo "^$VARIABLE=.*" "$CONFIG_FILE" | awk -F '=' '{print $2}')
    
    if [ "$current_value" != "$initial_value" ]; then
        echo "La variable $VARIABLE ha cambiado. Cerrando el programa..."
        pkill -f "$PYTHON_SCRIPT"
        exit 0
    fi
}

# Ejecutar el programa en Python
run_python_script &

# Monitorear cambios en la variable del archivo de configuración
while true; do
    sleep 1
    check_variable_changes
done
