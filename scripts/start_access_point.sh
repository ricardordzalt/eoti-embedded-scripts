#!/bin/bash

# Verificar si NetworkManager está en ejecución
if ! pgrep -x "NetworkManager" >/dev/null; then
    echo "NetworkManager is not running. Starting NetworkManager..."
    sudo systemctl start NetworkManager
    sudo systemctl enable NetworkManager
    echo "NetworkManager started and enabled."
fi

# Obtener el MAC address sin los dos puntos
mac_address=$(ifconfig wlan0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | sed 's/://g')

# Crear el SSID utilizando el MAC address
ssid="eoti-${mac_address}"

# Crear la contraseña utilizando el MAC address al revés
password=$(echo "${mac_address}" | rev)
echo "${mac_address}"
# echo "nmcli dev wifi hotspot ifname wlan0 ssid "${ssid}" password "${password}""
# Configurar el punto de acceso utilizando el SSID y la contraseña
nmcli dev wifi hotspot ifname wlan0 ssid "${ssid}" password "${password}"
