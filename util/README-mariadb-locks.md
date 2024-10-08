Yes, executing a query in MariaDB **can hold a lock** depending on the type of query and the current transaction state. Here's an explanation of when locks are held and how they are released:

### 1. **When Does the Lock Occur?**
- **SELECT Queries**: If you perform a simple `SELECT` query in a transaction with `REPEATABLE READ` or higher isolation level (the default for InnoDB), the query can create locks, especially if it's part of a transaction. It doesn't typically hold exclusive locks unless you use locking clauses like `FOR UPDATE` or `LOCK IN SHARE MODE`.
  
  - Example: 
    ```sql
    SELECT id FROM activity_table WHERE ip_address = '1.2.3.4' FOR UPDATE;
    ```
    This will place a **write lock** on the selected rows, preventing other transactions from updating them until you commit or rollback the transaction.

- **UPDATE, DELETE, INSERT Queries**: These types of queries will hold **write locks** on the affected rows (or, in some cases, the entire table) until the transaction is either committed or rolled back. The lock prevents other transactions from modifying the locked rows.

### 2. **How Long Does the Lock Last?**
- **Locks are held until the transaction is committed or rolled back**. 
  - If you are running within a transaction (even implicitly), locks will be held until `conn.commit()` or `conn.rollback()` is called.
  - If `autocommit` is **enabled** (which is the default for most connections), each query is treated as its own transaction, and the lock is released as soon as the query completes.

### 3. **Does `execute()` Hold the Lock?**
- When you call `cursor.execute()`, if the query involves an operation that modifies or reads data under specific conditions (like `SELECT ... FOR UPDATE`, `UPDATE`, `INSERT`, or `DELETE`), a lock is **acquired** and will be held until the transaction is completed (i.e., commit or rollback).
  
- If the `autocommit` is **disabled**, the lock is held until you explicitly commit the transaction with `conn.commit()` or rollback.

### 4. **What Happens with `SELECT` Queries?**
- **Read-only `SELECT`**: If you're just reading data and not using `FOR UPDATE` or `LOCK IN SHARE MODE`, no lock is typically held unless you're in a high isolation level (like `REPEATABLE READ`), where a read lock may be held for consistency. These locks are generally shared, meaning other transactions can still read the data but not modify it.
  
- **`SELECT ... FOR UPDATE`**: This will acquire a write lock on the selected rows to prevent other transactions from modifying them until the current transaction is complete.

### 5. **Autocommit and Transactions**:
- **With Autocommit Enabled (default)**:
  - Each query runs in its own transaction. After each `cursor.execute()` call, the transaction is automatically committed, and any locks are released immediately.
  
- **With Autocommit Disabled**:
  - Queries run within a transaction, and locks will be held until you explicitly commit or rollback. This allows multiple queries to run in the same transaction, but it also means locks can be held longer, which could cause issues like lock contention or deadlocks if other processes are trying to access the same rows.

### Example: Holding Locks in a Transaction

```python
import mysql.connector
from datetime import datetime

# Example connection to MariaDB
conn = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="your_database"
)

cursor = conn.cursor()

# Disable autocommit to manage transaction manually
conn.autocommit = False

# Start transaction, perform SELECT (which could acquire locks)
cursor.execute("SELECT id FROM activity_table WHERE ip_address = %s FOR UPDATE", (ip_address,))
record = cursor.fetchone()

if record:
    # If the IP address exists, update the datetime_of_last_ban
    update_query = '''
    UPDATE activity_table
    SET datetime_of_last_ban = %s
    WHERE ip_address = %s
    '''
    cursor.execute(update_query, (datetime.now(), ip_address))
else:
    # If the IP address doesn't exist, insert a new record
    insert_query = '''
    INSERT INTO activity_table (ip_address, usage_count, datetime_of_last_ban)
    VALUES (%s, 1, %s)
    '''
    cursor.execute(insert_query, (ip_address, datetime.now()))

# Commit the transaction, which releases the lock
conn.commit()

cursor.close()
conn.close()
```

In this example:
- The `SELECT ... FOR UPDATE` acquires a lock on the selected row.
- The lock is held until `conn.commit()` is called, at which point the lock is released.

### Recommendations:

- **Minimize Locking Time**: Always commit or rollback as soon as you're done with the critical section of your transaction to avoid holding locks longer than necessary.
  
- **Autocommit**: If you're performing a single operation, leaving `autocommit` enabled ensures that locks are held for the shortest possible time.

- **Use `FOR UPDATE`** only when necessary to avoid unnecessary locking.

### Conclusion:
- Yes, when you run `cursor.execute()` with certain types of queries (especially `UPDATE`, `DELETE`, `INSERT`, and `SELECT ... FOR UPDATE`), a lock is acquired, and it will be held until the transaction is committed or rolled back.
- If autocommit is disabled, the lock will persist until `conn.commit()` is called.

