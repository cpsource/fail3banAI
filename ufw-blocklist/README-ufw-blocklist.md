
## Use of ufw-blocklist

Parts of ufw-blocklist were used because it provides a clean, but faster 'ufw' interface that fail3ban can use to ban addresses.

We pickup speed because it uses an ipset, which is in linux kernel space.

Specifically, the authors modified after.init and placed it here. We no longer
loads the entire /etc/ipsum.4.txt, but rather we rely on ChatGPT to determine
threat level and then ban from there.

Further, 'ufw start', etc, is no longer required.

There are a number of .sh scripts in this directory. The name tells you what they do. To
get the entire list of possible commands, do a 'ipset -h'

## Requirements

```
  sudo apt install ipset
```

## Notes

### Interfearance with ufw

I haven't test what happens when you do a 'ufw start'. Presumably, you could modify after.init to use
a different set name that won't conflict with the one that's used by ufw.

### Poking Around

If you are timid like us, you can do:

```
  sudo ./after.init start
  sudo iptables -L -n
```

Ipset will be empty, but you've set it up to be loaded later. Your system won't be effected otherwise.

Then, to shut it down, do:

```
  sudo ./after.init stop
```
  
## References

https://github.com/poddmo/ufw-blocklist

