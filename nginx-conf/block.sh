#!/bin/sh
sudo iptables -A INPUT -p tcp -i venet0 --dport 8080 -j REJECT --reject-with tcp-reset
sudo iptables -A INPUT -s 198.35.46.0/24 -j DROP
sudo iptables -A INPUT -s 169.229.3.0/24 -j DROP

sudo iptables -L
