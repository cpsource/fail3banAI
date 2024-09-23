#!/bin/bash
sudo ipset restore < ../ufw-blocklist/rules.v4
sudo ipset restore < ../ufw-blocklist/rules.v6


