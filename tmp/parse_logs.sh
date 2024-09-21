#!/bin/bash
./parse_logs.py /var/log/auth.log > reports.csv && curl https://api.abuseipdb.com/api/v2/bulk-report -F csv=@reports.csv -H "Key: cccfb6429a3734c0d9b1b810209b0307e44d57fa9de06930b66d96c864f7463714a7d2adff63d0a5" > output.json
