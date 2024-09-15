
## Announcing fail3banAI

## What is fail3banAI ?

Fail3ban is an intrustion detection and prevention tool on ubuntu that uses the power of AI to
continuously adapt to an ever changing threat environment.

### Why do we need this intrustion tool anyway?

Just take a look at a snipit of my daily log file to see why:

```
United States : <time> <ip> xmlrpc.php[195689]: 'xmlrpc.php' executed by 34.122.181.129.
Russia        : <time> <ip> sshd[208904]: Connection closed by 78.29.41.83 port 54228 [preauth]
Indonesia     : <time> <ip> sshd[208907]: Connection closed by 103.157.114.66 port 37702
```

On the first line, someone from the US is probing for the existance of xmlrpc.php. It's used by WordPress
and others and is a threat point (that you should remove from your system!)

The second line shows someone in Russia probing sshd. ssh comonly uses port 22 by system administrators
to manage remote systems.

The third line shows someone from Indonesia trying the same port.

### Why do I need the power of AI?

You can add a table driven threat detector to your system, such as fail2ban, but it relies on
you, the system administrator to continuously monitor for threats and adjust the input tables.

With fail3banAI, none of this is necessary. Your faithful AI assistant is continually monitoring
your logs to detect intrustion attempts. When one is detected, fail3banAI adjusts itself and
begins monitoring for the new threat immediately.

### Prerequsites

You'll need to signup with openai.com for an API key. This author did so with a pay as you go plan. I deposited
$20.00 with them, and their system deducts a few pennies from this sum for every request I make.
When it runs out, I replunish it. For production though, you can use a higher dollar limit, or set the limit so high that you'd never hit it, yet still keep your costs under control.

fail3banAI is quite miserly with AI usage too. It will only make a request if it has not seen a particular threat
before. Then fail3banAI will ask if the log line is a threat at all. If not, no ban action will be taken, but the
request will be remembered, so as to not ask AI again. If AI comes back with yes, it's a threat, then fail3banAI
will ask for the control strings to monitor the threat. When these are returned fail3banAI incorporates
these into its control structures.






