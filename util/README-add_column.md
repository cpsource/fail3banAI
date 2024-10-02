# README-add_column.md

## Introduction

`add_column.py` is a Python script designed to help users easily modify SQLite3 databases by adding new columns to existing tables. The script is particularly useful when working with dynamic databases where schema changes may be required over time. This program ensures that column types are compatible with SQLite3 and provides safeguards to prevent the creation of duplicate columns or columns in non-existent tables.

## Prerequisites

Before running the script, ensure that:
- Python 3.x is installed on your system.
- The database you wish to modify is accessible.
- The environment variable `FAIL3BAN_PROJECT_ROOT` is set to the project root directory, where the SQLite3 database file is located.

## How It Works

The `add_column.py` script performs several checks before altering the database:
1. **Table existence**: Ensures the specified table exists in the database.
2. **Column duplication**: Checks whether the column already exists in the table to prevent duplication.
3. **Valid SQLite3 field types**: Ensures that the specified field type is valid for SQLite3.

If any of these checks fail, the script provides meaningful error messages and instructions on how to resolve the issue.

## Valid Field Types

The following field types are accepted by SQLite3 and supported by the script:
- `INTEGER`
- `TEXT`
- `BLOB`
- `REAL`
- `NUMERIC`
- `BOOLEAN`
- `DATE`
- `DATETIME`
- `CHAR`

## Usage

### Command Line Usage

To use the script, you must provide three arguments:
1. **Table Name**: The name of the table where you want to add the new column.
2. **Column Name**: The name of the new column you want to create.
3. **Column Type**: The data type for the new column.

### Syntax

```bash
python3 add_column.py <table_name> <column_name> <column_type>
```

### Example

To add a column named `age` of type `INTEGER` to a table called `users`, run:

```bash
python3 add_column.py users age INTEGER
```

This will modify the `users` table and add the `age` column, provided it doesn't already exist.

### Help and Table Listing

If the script is run without the correct arguments or if an invalid column type is used, it will display usage information and list the available tables in the SQLite database.

```bash
python3 add_column.py
```

Example output:

```
Usage: python3 add_column.py <table_name> <column_name> <column_type>

Valid SQLite3 field types:
 - INTEGER
 - TEXT
 - BLOB
 - REAL
 - NUMERIC
 - BOOLEAN
 - DATE
 - DATETIME
 - CHAR

Available tables in the database:
 - users
 - orders
 - logs
```

## Error Handling

The script checks for common errors and provides helpful messages:
- **Invalid Table**: If the table specified does not exist in the database.
- **Duplicate Column**: If the column you're trying to add already exists.
- **Invalid Field Type**: If the column type is not recognized by SQLite3.

If an error occurs, the script will not modify the database and will provide a clear error message.

## Conclusion

`add_column.py` is a powerful and user-friendly tool for modifying SQLite3 databases. By simplifying the process of adding new columns and ensuring schema integrity, it enhances the flexibility of your database management process.


