#!/bin/bash
sudo ip6tables -A ufw-blocklist-output -m limit --limit 5/min --limit-burst 10 -j LOG --log-prefix "DROP ufw-blocklist-input: " --log-level 4
sudo ip6tables -A ufw-blocklist-output -j DROP

