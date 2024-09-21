#!/bin/bash
curl -G https://api.abuseipdb.com/api/v2/blacklist -d confidenceMinimum=100 -d limit=9999999 -H "Key: cccfb6429a3734c0d9b1b810209b0307e44d57fa9de06930b66d96c864f7463714a7d2adff63d0a5" -H "Accept: application/json"
