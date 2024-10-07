#!/bin/bash

# This script goes back to the primary sources on the web, downloads their files,
# then build master-blacklist.ctl, then loads the resultant blacklist into
# ipsets
#

# Warning - we download set3 but call it 7 !!! It picks up about 8000+ more addresses
curl -sS -f --compressed -o ../control/ipsum.7.ctl 'https://raw.githubusercontent.com/stamparm/ipsum/master/levels/3.txt'

# get blacklist data from AbuseIPDB
python3 ./build-blacklist-4.py
python3 ./build-blacklist-6.py

# build master-blacklist.ctl
./sudoIt.sh ../lib/BlackList.py

# stop ipsets
sudo -E $(which python3) ../lib/ManageIpset4.py stop
sudo -E $(which python3) ../lib/ManageIpset6.py stop

# start ipsets
sudo -E $(which python3) ../lib/ManageIpset4.py start
sudo -E $(which python3) ../lib/ManageIpset6.py start

# load master-blacklist.ctl into ipset
./sudoIt.sh ./load-master-blacklist.py

# save a copy of kernel ipset to rules.v4 and rules.v6 
sudo ./ipset-save.sh
