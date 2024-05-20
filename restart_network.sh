#!/usr/bin/bash
# commented out method for older ubuntu
#sudo systemctl restart systemd-networkd
if [ -z "$1" ]; then
    iface=ens33
else
    iface=$1
fi
echo "Restarting network manager and interface $iface"
sudo systemctl restart NetworkManager && sudo ip link set $iface down && sudo ip link set $iface up
