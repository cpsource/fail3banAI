
# remove_iptabloes_rules.py

## Introduction

  This tool cleans up your iptables enteries after you stop the ufw tool.

## Run Instruction

Step 1: Make a z.log

```
	sudo -E iptables -L -n > z.log
```

Step 2: Edit z.log to remove any lines you don't want removed

Step 3: Run the tool

```
	sudo -E python3 remove_iptables_rules.py
```

Step 4: Verify the results

```
	sudo iptables -L -n
```

Note: The -E on the sudo command line is important. It keeps your current development
environment intact when the following commands are executed.
