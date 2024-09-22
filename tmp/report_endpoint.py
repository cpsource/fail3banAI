import requests
import json

# Defining the api-endpoint
url = 'https://api.abuseipdb.com/api/v2/report'

# String holding parameters to pass in json format
params = {
    'ip':'180.126.219.126',
    'categories':'18,20',
    'comment':'SSH login attempts with user root.'
    'timestamp':'2023-10-18T11:25:11-04:00'
}

headers = {
    'Accept': 'application/json',
    'Key': 'YOUR_OWN_API_KEY'
}

response = requests.request(method='POST', url=url, headers=headers, params=params)

# Formatted output
decodedResponse = json.loads(response.text)
print json.dumps(decodedResponse, sort_keys=True, indent=4)


ID	Title	Description
1	DNS Compromise	Altering DNS records resulting in improper redirection.
2	DNS Poisoning	Falsifying domain server cache (cache poisoning).
3	Fraud Orders	Fraudulent orders.
4	DDoS Attack	Participating in distributed denial-of-service (usually part of botnet).
5	FTP Brute-Force
6	Ping of Death	Oversized IP packet.
7	Phishing	Phishing websites and/or email.
8	Fraud VoIP
9	Open Proxy	Open proxy, open relay, or Tor exit node.
10	Web Spam	Comment/forum spam, HTTP referer spam, or other CMS spam.
11	Email Spam	Spam email content, infected attachments, and phishing emails. Note: Limit comments to only relevent information (instead of log dumps) and be sure to remove PII if you want to remain anonymous.
12	Blog Spam	CMS blog comment spam.
13	VPN IP	Conjunctive category.
14	Port Scan	Scanning for open ports and vulnerable services.
15	Hacking
16	SQL Injection	Attempts at SQL injection.
17	Spoofing	Email sender spoofing.
18	Brute-Force	Credential brute-force attacks on webpage logins and services like SSH, FTP, SIP, SMTP, RDP, etc. This category is seperate from DDoS attacks.
19	Bad Web Bot	Webpage scraping (for email addresses, content, etc) and crawlers that do not honor robots.txt. Excessive requests and user agent spoofing can also be reported here.
20	Exploited Host	Host is likely infected with malware and being used for other attacks or to host malicious content. The host owner may not be aware of the compromise. This category is often used in combination with other attack categories.
21	Web App Attack	Attempts to probe for or exploit installed web applications such as a CMS like WordPress/Drupal, e-commerce solutions, forum software, phpMyAdmin and various other software plugins/solutions.
22	SSH	Secure Shell (SSH) abuse. Use this category in combination with more specific categories.
23	IoT Targeted	Abuse was targeted at an "Internet of Things" type device. Include information about what type of device was targeted in the comments.

