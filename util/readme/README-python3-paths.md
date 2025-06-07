Yes, Python uses several environment variables to control the behavior of its interpreter, including the **library include path**. If you want to globally control where Python looks for modules and packages, you can use the following environment variables:

### 1. **`PYTHONPATH`**:
   - **Purpose**: `PYTHONPATH` is an environment variable that you can set to specify additional directories where Python should look for modules and packages. It works similarly to the system's `PATH` variable, but it applies to Python modules.
   - **Usage**: You can add custom directories to `PYTHONPATH`, and Python will include those directories when searching for imports.
   - **Syntax**: The format is a colon-separated (`:`) list of directories on Unix-like systems (Linux/macOS) and a semicolon-separated (`;`) list on Windows.

#### Example (Unix-like systems):
```bash
export PYTHONPATH=/path/to/your/library:/another/path
```

#### Example (Windows):
```bash
set PYTHONPATH=C:\path\to\your\library;C:\another\path
```

#### Example in Python:
```python
import sys
print(sys.path)  # This will include directories from PYTHONPATH if set
```

`PYTHONPATH` is used in addition to the default locations that Python searches for modules (like the `site-packages` directory).

### 2. **`PYTHONHOME`**:
   - **Purpose**: `PYTHONHOME` is an environment variable that can be used to set an alternate location for the standard Python libraries. It affects where Python looks for its standard library modules (like `os`, `sys`, etc.).
   - **Usage**: This variable is typically used when embedding Python or for virtual environments where you want to set a different root directory for Python's installation.

#### Example (Unix-like systems):
```bash
export PYTHONHOME=/path/to/your/python/environment
```

### 3. **`PYTHONSTARTUP`**:
   - **Purpose**: This environment variable points to a file that Python will execute every time the interpreter starts. While this is not directly related to the module include path, it can be used to modify `sys.path` on startup.
   - **Usage**: You can modify `sys.path` in the script pointed to by `PYTHONSTARTUP` to include custom directories.

#### Example:
```bash
export PYTHONSTARTUP=/path/to/your/startup/script.py
```

In the `startup/script.py`, you could add:
```python
import sys
sys.path.append('/path/to/your/library')
```

### Checking Python's Library Path at Runtime:
You can always check where Python is looking for modules at runtime by inspecting `sys.path`. This will show you the directories Python searches when importing modules, including any directories set by `PYTHONPATH`.

```python
import sys
print(sys.path)
```

### Summary:
- **`PYTHONPATH`**: Use this to add custom directories where Python will search for modules globally.
- **`PYTHONHOME`**: Use this to change the root directory of Python's standard library.
- **`PYTHONSTARTUP`**: Use this to run a script at startup, which can modify `sys.path`.

If you're configuring a global environment where Python modules will be installed in custom locations, setting `PYTHONPATH` is usually the best approach.

Let me know if you need further clarification or additional examples!
