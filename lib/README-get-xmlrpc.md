On the question line: on a web site, if someone did a GET /xmlrpc.php, what are they trying to do
I received this response:

A **`GET /xmlrpc.php`** request is commonly an attempt to interact with the **XML-RPC API** of a WordPress site. This file is part of WordPress' default installation and enables remote procedures like publishing content, making changes, or handling communication with third-party applications (such as mobile apps or plugins).

However, **`xmlrpc.php`** has become a frequent target for malicious activity, particularly for the following reasons:

1. **Brute Force Attacks**: Attackers often target `xmlrpc.php` to attempt brute-force login attacks by sending repeated XML-RPC requests to guess login credentials.
   
2. **DDoS Amplification**: The XML-RPC protocol allows for "pingback" features, which attackers can exploit to amplify Distributed Denial of Service (DDoS) attacks, using the `xmlrpc.php` file to flood a target server.

3. **Exploiting Vulnerabilities**: Some attacks leverage vulnerabilities in plugins or in the XML-RPC protocol itself to execute remote code or compromise a site.

### Recommended Actions:
- If `xmlrpc.php` is not needed, you may want to disable or block access to it using `.htaccess` or firewall rules to prevent unauthorized access and mitigate potential threats.

### Source:
- [WordPress.org XML-RPC](https://wordpress.org/support/article/xml-rpc/)