#!/bin/bash

# Display iptables rules for all chains
echo "=== IPTABLES STATUS ==="

# Show the raw table
echo "----- RAW TABLE -----"
iptables -t raw -L -v -n --line-numbers

# Show the filter table (default table)
echo "----- FILTER TABLE -----"
iptables -t filter -L -v -n --line-numbers

# Show the nat table
echo "----- NAT TABLE -----"
iptables -t nat -L -v -n --line-numbers

# Show the mangle table
echo "----- MANGLE TABLE -----"
iptables -t mangle -L -v -n --line-numbers

# Show the security table (if available)
echo "----- SECURITY TABLE -----"
iptables -t security -L -v -n --line-numbers

echo "====================="

