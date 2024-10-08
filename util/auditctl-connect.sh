#sudo auditctl -a always,exit -F arch=b64 -S connect -k network-connect

#sudo ausearch -k network-connect

# -a always,exit -F arch=b64 -S connect -k network-activity
# -w /etc/passwd -p wa -k passwd_changes
# -w /var/log/ -p wa -k log_monitoring

# monitor sendto and sendmsg
# sudo auditctl -a always,exit -F arch=b64 -S sendto -k sendto-monitoring
# sudo auditctl -a always,exit -F arch=b64 -S sendmsg -k sendmsg-monitoring
# sudo auditctl -a always,exit -F arch=b64 -S socket -F a0=2 -F a1=3 -k raw-socket-monitoring
# sudo auditctl -a always,exit -F arch=b64 -S accept -k accept-monitoring
# sudo auditctl -w /usr/sbin/iptables -p x -k iptables-monitoring

# monitor udp
# sudo auditctl -a always,exit -F arch=b64 -S sendto -S sendmsg -F a0=2 -k udp-out-ipv4
# sudo auditctl -a always,exit -F arch=b64 -S sendto -S sendmsg -F a0=10 -k udp-out-ipv6

# delete
# sudo auditctl -d always,exit -F arch=b64 -S connect -k network-connect
#
# or
#
# sudo auditctl -D 0
#
# Delete All Rules
# sudo auditcll -D
#
# see /etc/audit ... for perminant rules, etc
#

#
# current monitoring setup
#

sudo auditctl -a always,exit -F arch=b64 -S connect -k network-connect
sudo auditctl -a always,exit -F arch=b64 -S sendto -k sendto-monitoring
sudo auditctl -a always,exit -F arch=b64 -S sendmsg -k sendmsg-monitoring
sudo auditctl -a always,exit -F arch=b64 -S socket -F a0=2 -F a1=3 -k raw-socket-monitoring

#
# and show
#
sudo auditctl -l

# To decode strings, use
# cat 'str' | xxd -r -p

#
# for failure status
#
echo "*** network-connect"
sudo ausearch -k network-connect | egrep -H -e "success=no"
echo "*** sendto-monitoring"
sudo ausearch -k sendto-monitoring | egrep -H -e "success=no"
echo "*** sendmsg-monitoring"
sudo ausearch -k sendmsg-monitoring | egrep -H -e "success=no"
echo "*** raw-socket-monitoring"
sudo ausearch -k raw-socket-monitoring | egrep -H -e "success=no"
echo "*** udp-out-ipv4"
sudo ausearch -k udp-out-ipv4 | egrep -H -e "success=no"
echo "*** udp-out-ipv6"
sudo ausearch -k udp-out-ipv6 | egrep -H -e "success=no"

#
# fork and vfork
# sudo auditctl -a always,exit -F arch=b64 -S fork -S vfork -k process_creation
# execve
# sudo auditctl -a always,exit -F arch=b64 -S execve -k exec_events
