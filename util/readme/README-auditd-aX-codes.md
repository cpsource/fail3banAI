In **auditd** rules, the **`aX` codes** refer to the **system call arguments** passed to the system calls. Each system call typically accepts multiple arguments, and **`a0`, `a1`, `a2`, ...** are placeholders for these arguments. These arguments represent memory addresses, file descriptors, flags, or other values used by system calls.

Here’s a breakdown of what each **`aX`** represents:

### General Structure of System Call Arguments:

- **`a0`**: The **first argument** of the system call.
- **`a1`**: The **second argument**.
- **`a2`**: The **third argument**.
- **`a3`**: The **fourth argument**.
- **`a4`, `a5`, `a6`**, etc., if applicable: Additional arguments.

The number of arguments depends on the system call being audited. For example, the **`connect()`** system call has three arguments, while **`open()`** typically has two.

### How `aX` is Used in `auditctl` Rules:

When creating an audit rule with **`auditctl`**, you can filter based on these system call arguments (i.e., `a0`, `a1`, etc.) to track certain behaviors or conditions for that system call.

### Example: `connect()` System Call

Let’s break down an example of the `connect()` system call:

```c
int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
```

- **`a0` (sockfd)**: The first argument is the **socket file descriptor**.
- **`a1` (addr)**: The second argument is the **socket address** (a pointer to the address structure).
- **`a2` (addrlen)**: The third argument is the **length of the address**.

### Example: Audit Rule for `connect()`

If you wanted to audit the `connect()` system call for IPv4 connections (where `a0` is the address family `AF_INET`, which has the numeric value `2`), the rule would look like this:

```bash
sudo auditctl -a always,exit -F arch=b64 -S connect -F a0=2 -k connect-ipv4
```

- **`-S connect`**: Audits the `connect()` system call.
- **`-F a0=2`**: Filters for the first argument (`a0`) of the `connect()` call, which represents the **address family** (IPv4 in this case, as `AF_INET` equals `2`).

### Example: `sendto()` System Call

Here’s an example of a **`sendto()`** system call:

```c
ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);
```

- **`a0` (sockfd)**: The first argument is the **socket file descriptor**.
- **`a1` (buf)**: The second argument is the **buffer** that holds the data to be sent.
- **`a2` (len)**: The third argument is the **length of the data**.
- **`a3` (flags)**: The fourth argument is the **flags** used for sending.

You can audit based on any of these arguments.

### Example: Auditing `sendto()` for UDP (IPv4)

If you wanted to audit outgoing UDP packets sent using the `sendto()` system call for IPv4, you would audit based on the **address family** argument (`a0=2` for `AF_INET`):

```bash
sudo auditctl -a always,exit -F arch=b64 -S sendto -F a0=2 -k sendto-ipv4
```

- **`-F a0=2`**: Filters for the first argument of the `sendto()` call, which specifies IPv4 (`AF_INET`).

### Argument Filter (aX) Reference:

- **`a0`**: The first argument passed to the system call.
- **`a1`**: The second argument passed to the system call.
- **`a2`**: The third argument passed to the system call.
- **`a3`**: The fourth argument passed to the system call.

Each system call has its own specific arguments, and you can look up the system call in **man pages** (e.g., `man 2 connect`) to understand what each argument does. 

### Practical Use:

You would use these `aX` codes when you want to audit a system call based on specific parameters. For example, to audit only certain system calls with specific flags or for a specific socket family.

### Conclusion:

- **`a0`, `a1`, `a2`, etc.**: These are placeholders for the arguments passed to a system call. 
- **`a0=2`**: For example, means the first argument (`a0`) is equal to `2`, which could represent `AF_INET` (IPv4) in a socket-related call.

Let me know if you need more information or examples based on a specific system call!
