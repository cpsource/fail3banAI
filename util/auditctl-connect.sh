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
sudo auditctl -l
