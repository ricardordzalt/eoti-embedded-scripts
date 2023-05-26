#!/bin/bash

# Obtener la dirección MAC del dispositivo
#mac_address=$(cat /sys/class/net/wlan0/address)
mac_address="00:1a:2b:3c:4d:5e"
mac_address=${mac_address//:/}  # Eliminar los dos puntos ":" de la dirección MAC
reversed_mac=$(echo $mac_address | rev)  # Revertir la dirección MAC
ssid="eoti$reversed_mac"  # Concatenar "eoti" y la dirección MAC invertida


# Configurar el punto de acceso en el archivo de configuración de hostapd
sudo sed -i '' 's/^#interface=.*$/interface=wlan0/' /etc/hostapd/hostapd.conf
sudo sed -i '' 's/^#driver=.*$/driver=nl80211/' /etc/hostapd/hostapd.conf
sudo sed -i '' 's/^#ssid=.*$/ssid='"$ssid"'/' /etc/hostapd/hostapd.conf
sudo sed -i '' 's/^#hw_mode=.*$/hw_mode=g/' /etc/hostapd/hostapd.conf
sudo sed -i '' 's/^#channel=.*$/channel=6/' /etc/hostapd/hostapd.conf
sudo sed -i '' 's/^#wpa=.*$/wpa=1/' /etc/hostapd/hostapd.conf
sudo sed -i '' 's/^#wpa_passphrase=.*$/wpa_passphrase='"$reversed_mac"'/' /etc/hostapd/hostapd.conf

# Configurar la interfaz WLAN0 en el archivo de configuración de red
sudo sed -i '/^iface wlan0/,/^$/d' /etc/network/interfaces
sudo sed -i '/^wpa-conf /d' /etc/network/interfaces
sudo sed -i '/^up iptables/d' /etc/network/interfaces
sudo sed -i '/^down iptables/d' /etc/network/interfaces

# Configurar la dirección IP estática para el punto de acceso
echo -e "interface wlan0\n\tstatic ip_address=192.168.4.1/24" | sudo tee -a /etc/dhcpcd.conf > /dev/null

# Configurar el servicio dnsmasq para el punto de acceso
echo -e "interface=wlan0\ndhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" | sudo tee /etc/dnsmasq.conf > /dev/null

# Habilitar el enrutamiento IP
sudo sed -i 's/^#net.ipv4.ip_forward=1$/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

# Configurar iptables para el enrutamiento de paquetes
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Configurar el servicio para cargar las reglas de iptables en el arranque
sudo sed
