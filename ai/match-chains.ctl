[subroutine: invalid_user]
match_date
match_ip
match_jail
match_user_invalid_user
match_ip_address
match_port

[subroutine: connection_closed]
match_date
match_ip
match_jail
match_user_connection_closed
match_ip_address
match_port

# Sep 13 08:23:51 ip-172-26-10-222 sshd[147882]: User nobody from 65.20.164.43 not allowed because not listed in AllowUsers
[subroutine: block_nobody_user]
match_date
match_ip
match_jail
match_user_not_allowed


