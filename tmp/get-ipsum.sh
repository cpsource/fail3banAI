#!/bin/bash
curl --compressed https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt 2>/dev/null | grep -v "#" | grep -v -E "\s[1-2]$" | cut -f 1 > ipsum-filtered.txt
curl --compressed https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt 2>/dev/null > ipsum.txt
#
# get the current level 4 banned list
#
curl -sS -f --compressed -o ipsum-new.4.txt 'https://raw.githubusercontent.com/stamparm/ipsum/master/levels/4.txt'
