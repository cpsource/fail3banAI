In general, MariaDB (and MySQL) will automatically use indexes when they help speed up queries, especially when you query by indexed columns like `ip_address`. However, there are a few things to ensure that the index is properly used:

### 1. **Correct Query Format:**
   The query must be structured in a way that encourages the database to use the index. For example, a simple query like this:

   ```sql
   SELECT * FROM ip_responses WHERE ip_address = '192.168.1.1';
   ```

   This query should automatically utilize the `idx_ip_address` index to speed up lookups for `ip_address`.

### 2. **Check the Query Plan:**
   You can verify that the index is being used by running an `EXPLAIN` on your query. This will show you whether MariaDB is using the index or not:

   ```sql
   EXPLAIN SELECT * FROM ip_responses WHERE ip_address = '192.168.1.1';
   ```

   In the output of `EXPLAIN`, look at the `key` column. It should list `idx_ip_address`, meaning the index is being used.

### 3. **Make Sure the Query Uses the Exact Indexed Column:**
   If you apply functions to `ip_address` or use a pattern search (like `LIKE '%...'`), it can prevent the index from being used efficiently. For example:

   ```sql
   SELECT * FROM ip_responses WHERE LOWER(ip_address) = '192.168.1.1';
   ```

   This query would **not** use the index because of the `LOWER()` function. If you query `ip_address` as it is without functions, the index is more likely to be used.

### 4. **Check for Sargable Queries:**
   Make sure that your query is "sargable" (Search ARGument ABLE), meaning that it allows MariaDB to use indexes efficiently. For example, the following query might not use the index efficiently:

   ```sql
   SELECT * FROM ip_responses WHERE SUBSTRING(ip_address, 1, 3) = '192';
   ```

   This is non-sargable because it applies a function (`SUBSTRING()`) to the indexed column, meaning the index will likely be bypassed.

   Instead, query directly with comparison operators, which will likely use the index:

   ```sql
   SELECT * FROM ip_responses WHERE ip_address LIKE '192%';
   ```

### 5. **Query Optimization:**
   MariaDB will automatically decide whether or not to use an index based on its internal query optimizer. If the optimizer determines that a full table scan is faster than using the index (e.g., if there are very few rows in the table or the query is expected to return a large percentage of the rows), it may not use the index.

### 6. **Force the Index (Optional):**
   If you suspect MariaDB is not using the index when it should, you can force it to use the index by using the `FORCE INDEX` clause:

   ```sql
   SELECT * FROM ip_responses FORCE INDEX (idx_ip_address) WHERE ip_address = '192.168.1.1';
   ```

   This tells MariaDB explicitly to use the `idx_ip_address` index.

### Conclusion:
You generally don’t need to do anything special to make MariaDB use the index on `ip_address`. MariaDB’s query optimizer will automatically use it when appropriate. However, using `EXPLAIN` to check if the index is being used and making sure your queries are structured properly can help ensure the index is leveraged for performance optimization.
