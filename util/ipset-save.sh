#!/bin/bash
sudo ipset save ufw-blocklist-ipsum > ../ufw-blocklist/rules.v4
sudo ipset save ufw-blocklist6-ipsum > ../ufw-blocklist/rules.v6
chmod 440 ../ufw-blocklist/rules.v4
chmod 440 ../ufw-blocklist/rules.v6

