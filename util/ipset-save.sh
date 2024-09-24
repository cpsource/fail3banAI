#!/bin/bash
ipset save ufw-blocklist-ipsum > ../ufw-blocklist/rules.v4
ipset save ufw-blocklist6-ipsum > ../ufw-blocklist/rules.v6
chmod 444 ../ufw-blocklist/rules.v4
chmod 444 ../ufw-blocklist/rules.v6
