To see the methods supported by an object in Python, you can use the built-in `dir()` function. This function returns a list of all attributes and methods (both built-in and user-defined) available for an object.

Here’s an example:

```python
my_object = SomeClass()

# See the list of methods and attributes supported by the object
print(dir(my_object))
```

If you want to filter out the special methods (methods starting and ending with double underscores, like `__init__`), you can do something like this:

```python
methods = [method for method in dir(my_object) if not method.startswith('__')]
print(methods)
```

To get more detailed information about a specific method, such as its documentation, you can use the `help()` function:

```python
help(my_object.some_method)
```

This will display the docstring for `some_method` if it's available.

Would you like help with a specific object in your code?
