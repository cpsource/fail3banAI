#!/bin/bash

# Check if Developer_IP is set, if not exit the script without a message
if [ -z "$Developer_IP" ]; then
    echo "Environmental variable Developer_IP is not set. Exiting."
    exit 0
fi

# Use Developer_IP as the IP to be added
IP="$Developer_IP"

echo "$(date '+%Y-%m-%d %H:%M:%S') - open-developer-port set $Developer_IP" >> ~/open-developer-port.log

# Get the first rule in the INPUT chain (third line in the iptables output)
first_rule=$(sudo iptables -L INPUT --line-numbers -n | sed -n '3p')

# Define the exact rule we're looking for, including the IP address
exact_rule="ACCEPT     all  --  $IP"

# Check if the first rule exactly matches the desired rule (including the IP)
if echo "$first_rule" | grep -q "ACCEPT.*$IP"; then
    echo "  The first rule in the INPUT chain is an exact match. No changes needed." >> ~/open-developer-port.log
    # Say we are done
    echo " Script completed" >> ~/open-developer-port.log
    exit 0
fi

# Define the rule pattern (excluding the IP address)
rule_pattern="ACCEPT"

# Check if the first rule matches the pattern (ignoring the IP address)
if echo "$first_rule" | grep -q "$rule_pattern"; then
    echo "  The first rule in the INPUT chain matches the desired rule (ignoring IP). Deleting it..." >> ~/open-developer-port.log
    
    # Delete the first rule
    sudo iptables -D INPUT 1
    echo "  First rule deleted." >> ~/open-developer-port.log
fi

# Add the rule at position 1 with the correct IP
sudo iptables -I INPUT 1 -s $IP -j ACCEPT
echo "  Rule for $IP added at position 1 in the INPUT chain." >> ~/open-developer-port.log

# Say we are done
echo " Script completed" >> ~/open-developer-port.log
