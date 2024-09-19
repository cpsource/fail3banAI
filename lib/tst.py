
import ShortenJournalString

sjs = ShortenJournalString.ShortenJournalString()

line =  "Sep 19 08:30:12 ip-172-26-10-222 sshd[27642]: Disconnected from user ubuntu 98.97.16.226 port 22216:22"

#line = "Sep 19 09:45:03 ip-172-26-10-222 amazon-ssm-agent.amazon-ssm-agent[445]: 2024-09-19 09:45:03 WARN EC2RoleProvider Failed to connect to Systems Manager with instance profile role credentials. Err: retrieved credentials failed to report to ssm. RequestId: 0f744f29-24c0-447e-b2a8-ec11e24caa56 Error: AccessDeniedException: User: arn:aws:sts::230858838317:assumed-role/AmazonLightsailInstanceRole/i-074053a9ee2ed2380 is not authorized to perform: ssm:UpdateInstanceInformation on resource: arn:aws:ec2:us-east-1:230858838317:instance/i-074053a9ee2ed2380 because no identity-based policy allows the ssm:UpdateInstanceInformation action"


found_items, shortened_string = sjs.shorten_string(line)

print(f"\nline: {line}\n\nfound_items: {found_items}\n\n shortened_string = {shortened_string}")

