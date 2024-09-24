#!/bin/bash

# This script goes back to the primary sources on the web, downloads their files,
# then build master-blacklist.ctl, then loads the resultant blacklist into
# ipsets
#

curl -sS -f --compressed -o ../control/ipsum.7.ctl 'https://raw.githubusercontent.com/stamparm/ipsum/master/levels/7.txt'
python3 ./build-blacklist-4.py
python3 ./build-blacklist-6.py
./sudoIt.sh ../lib/blacklist.py

# load master-blacklist.ctl into ipset

./sudoIt.sh ./load-master-blacklist.py

# save
sudo ./ipset-save.sh
