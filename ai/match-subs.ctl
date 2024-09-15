[subroutine: match_date]
(?P<date>\w+\s+\d+\s+\d{2}:\d{2}:\d{2})\s+

[subroutine: match_ip]
[ \t]*ip-[0-9]+-[0-9]+-[0-9]+-[0-9]+[ \t]*

[subroutine: match_jail]
(?P<jail>[a-zA-Z0-9]+)\[\d+\]:\s+

[subroutine: match_user_invalid_user]
Invalid\s+user\s+(?P<user>\w+)\s+from\s+

[subroutine: match_user_connection_closed]
Connection\s+closed\s+by\s+invalid\s+user\s+(?P<user>\w+)

[subroutine: match_ip_address]
(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+

[subroutine: match_port]
port\s+(?P<port>\d+)\s*

[subroutine: match_user_not_allowed]
User\s+(?P<user>\w+)\s+from\s+(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+not\s+allowed\s+because\s+not\s+listed\s+in\s+AllowUsers

