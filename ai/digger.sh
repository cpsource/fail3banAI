#!/bin/bash

# Check if IP address is passed as a command-line argument
if [ -z "$1" ]; then
    echo "Usage: $0 <ip_address>"
    exit 1
fi

IP_ADDRESS=$1

# Echo and run the first dig command
echo "Running: dig +noall +answer $IP_ADDRESS"
dig +noall +answer $IP_ADDRESS

# Echo and run the reverse DNS lookup
echo "Running: dig -x $IP_ADDRESS +noall +answer"
dig -x $IP_ADDRESS +noall +answer

# Echo and run the dig trace
echo "Running: dig $IP_ADDRESS +trace"
dig $IP_ADDRESS +trace

