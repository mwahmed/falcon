#!/bin/bash

echo "Opening port 3000"
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT

echo "Opening port 8080"
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
