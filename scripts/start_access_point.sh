#!/bin/bash

# Obtener el MAC address sin los dos puntos
mac_address=$(ifconfig | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | sed 's/://g')

# Crear el SSID utilizando el MAC address
ssid="eoti-${mac_address}"

# Crear la contraseña utilizando el MAC address al revés
password=$(echo "${mac_address}" | rev)

# Configurar el punto de acceso utilizando el SSID y la contraseña
nmcli dev wifi hotspot ifname wlan0 ssid "${ssid}" password "${password}"
