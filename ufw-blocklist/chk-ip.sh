#!/bin/bash

#make a bash script out of this curl bit. Get the key from environmental var ABUSEIPDB_KEY.
#Take one argument on the command line, this ip address: # The -G option will convert form parameters (-d options) into query parameters.
# The CHECK endpoint is a GET request.
curl -G https://api.abuseipdb.com/api/v2/check \
  --data-urlencode "ipAddress=125.143.213.84" \
  -d maxAgeInDays=90 \
  -d verbose \
  -H "Key: $ABUSEIPDB_KEY" \
  -H "Accept: application/json"
