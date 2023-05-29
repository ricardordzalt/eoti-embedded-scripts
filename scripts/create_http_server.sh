#!/bin/bash

# Ruta al archivo de configuración
CONFIG_FILE="$HOME/.eoti/local.conf"

# Ruta al programa en Python
PYTHON_SCRIPT="create_http_server.py"

# Variable a monitorear
VARIABLE="is_auth"
is_auth="0"

# Obtener el valor inicial de la variable del archivo de configuración
initial_value=$(grep -Eo "^$VARIABLE=.*" "$CONFIG_FILE" | awk -F '=' '{print $2}')

# Verificar si la variable está definida en el archivo de configuración
if [ -z "$initial_value" ]; then
    # Variable no definida, inicializarla en false
    echo "$VARIABLE=false" >> "$CONFIG_FILE"
else
    # Variable definida, cambiarla a false
    awk -v var="$VARIABLE=false" '/^'"$VARIABLE"'=/{ $0=var }1' "$CONFIG_FILE" > tmpfile && mv tmpfile "$CONFIG_FILE"
fi

# Función para ejecutar el programa en Python
run_python_script() {
    python3 "$PYTHON_SCRIPT"
}

# Función para comprobar si la variable ha cambiado en el archivo de configuración
check_variable_changes() {
    current_value=$(grep -Eo "^$VARIABLE=.*" "$CONFIG_FILE" | awk -F '=' '{print $2}')
    
    if [ "$current_value" = "true" ]; then
        echo "Logged succesful"
        pkill -f "$PYTHON_SCRIPT"
        is_auth="1"
    fi
}

# Ejecutar el programa en Python
run_python_script &

# Monitorear cambios en la variable del archivo de configuración
while [ "$is_auth" -eq 0 ]; do
    sleep 1
    check_variable_changes
done
