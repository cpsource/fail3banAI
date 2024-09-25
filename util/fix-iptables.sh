#!/bin/bash

# Check if the chain argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <chain>"
  exit 1
fi

CHAIN="$1"
CMD="iptables"

# Delete the first rule in the chain
$(CMD) -D "$CHAIN" 1

# Add the LOG rule as the first element in the chain
$(CCMD) -I "$CHAIN" 1 -m limit --limit 5/min --limit-burst 10 -j LOG --log-prefix "zDROP $CHAIN: " --log-level 4

$(CMD) -L -v -n

echo "First rule deleted and LOG rule added to chain $CHAIN."

