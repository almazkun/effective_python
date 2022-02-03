# Chapter 8. Robustness and Performance

After a program does what you need, one can start make it robust, making it dependable when faced with unexpected circumstances, and make it performant, making it possible to handle non-trivial amounts of data.

Python may help you achieve this with minimal effort.

## Item 65: Take Advantage of Each Block in `try/except/else/finally`

There are four distinct times when one can act during exception handling. With each block serving an unique purpose.

### `finally` block
Use `try/finally` when it is needed for the exception to propagate but also to make some cleanup to happen. Like closing file handle:
```py
def try_finally_example(filename):
    print(" * Open file")
    handle = open(filename, encoding='utf-8') # OSError may happen
    try:
        print(" * Read file")
        return handle.read() # UnicodeDecodeError may happen
    finally:
        print(" * Close file")
        handle.close() # Always executed after `try` block
```
Any exception raised in `try` block will be propagated to the caller but `finally` block will be executed first. 
```py
filename = "file.txt"

with open(filename, "wb") as f:
    f.write(b"Hello, world!")

data = try_finally_example(filename)
```
    >>>
     * Open file
     * Read file
     * Close file
    Traceback (most recent call last):
    File "main.py", line 17, in <module>
        data = try_finally_example(filename)
    File "main.py", line 6, in try_finally_example
        return handle.read() # UnicodeDecodeError may happen
    File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.8/lib/python3.8/codecs.py", line 322, in decode
        (result, consumed) = self._buffer_decode(data, self.errors, final)
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1 in position 0: invalid continuation byte

One must call open before `try` block, because if its raises an exception, `finally` block should be ignored entirely.
```
try_finally_example('does_not_exist.txt')
```
    >>>
     * Open file
    Traceback (most recent call last):
    File "main.py", line 12, in <module>
        try_finally_example('does_not_exist.txt')
    File "main.py", line 3, in try_finally_example
        handle = open(filename, encoding='utf-8') # OSError may happen
    FileNotFoundError: [Errno 2] No such file or directory: 'does_not_exist.txt'

#### `else` Blocks
Using `try\except\else` blocks makes it clear which exception will be handled by your code and which will propagate up. When `try` block `DOES NOT` raises an exception, `else` block will be executed. For example you want to load a `JSON` data from a string and return a value of the key:
```py
import json

deg load_json_key(data, key):
    try:
        print(" * Load JSON")
        result_dict =  json.loads(data) # May raise value error
    except ValueError as e:
        print(" * Handling ValueError")
        return KeyError(key) from e
    else:
        print(" * Key look up")
        return result_dict[key]

assert load_json_key('{"foo": "bar"}', 'foo') == 'bar'
```
    >>>
     * Load JSON
     * Key look up

When ValueError is raised, `except` block will handle the exception and return a KeyError.
```py
load_json_key('{"foo": bad payload', 'foo')
```
    >>>
     * Load JSON
     * Handling ValueError
    Traceback (most recent call last):
    ...
    json.decoder.JSONDecodeError: Expecting value: line 1 column 9 (char 8)
    ...
    Traceback (most recent call last):
    ...
    KeyError: 'foo'

If the key look up rises any exceptions, they will propagate to the caller and they will be visually distinguished from `except` block errors, this will make exception propagation behavior clearer.

```py
load_json_key('{"foo": "bar"}', 'does not exist')
```
    >>>
     * Load JSON
     * Key look up
    Traceback (most recent call last):
    ...
    KeyError: 'does not exist'

#### Everything Together
`try/except/else/finally` for example, you want to read the file, process it and update the file in-place:
```py
UNDEFINED = object()

def divide_json(path):
    print(" * Open file")
    handle = open(path, "r+")  # OSError may happen
    try:
        print(" * Read file")
        data = handle.read()  # UnicodeDecodeError may happen
        print(" * Parse JSON")
        op = json.loads(data)  # ValueError may happen
        print(" * Divide")
        value = op["numerator"] / op["denominator"]  # ZeroDivisionError may happen
    except ZeroDivisionError as e:
        print(" * Handling ZeroDivisionError")
        return UNDEFINED
    else:
        print(" * Update file")
        op["result"] = value
        result = json.dumps(op)
        handle.seek(0)  # OSError may happen
        handle.write(result)  # OSError may happen
        return value
    finally:
        print(" * Close file")
        handle.close()  # Always executed
```

In successful case, `try\else\finally` blocks will run:
```py
temp_path = "random_data.json"
with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 10}')
assert divide_json(temp_path) == 0.1
```
    >>>
     * Open file
     * Read file
     * Parse JSON
     * Divide
     * Update file
     * Close file

If calculation is invalid, `try\except\finally` blocks will run:
```py
temp_path = "random_data.json"
with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 0}')
assert divide_json(temp_path) == UNDEFINED
```
    >>>
     * Open file
     * Read file
     * Parse JSON
     * Divide
     * Handling ZeroDivisionError
     * Close file

If the JSON data in invalid, `try\finally` blocks will run and exceptions will propagate up:
```py
with open(temp_path, 'w') as f:
    f.write('{"numerator": 1 bad data')
divide_json(temp_path)
```
    >>>
     * Open file
     * Read file
     * Parse JSON
     * Close file
    Traceback (most recent call last):
    ...
    json.decoder.JSONDecodeError: Expecting ',' delimiter: line 1 column 17 (char 16)

This layout is very useful because all the blocks work together in the intuitive way. For example, this is how unexpected `OSError` is handled:
```py
with open(temp_path, 'w') as f:
     f.write('{"numerator": 1, "denominator": 10}')
divide_json(temp_path)
```
    >>>>>>
     * Open file
     * Read file
     * Parse JSON
     * Divide
     * Update file
     * Close file
    Traceback ...
    OSError: [Errno 28] No space left on device

## Item 66: Consider `contextlib` and `with` Statements for Reuseable `try/finally` Behavior

The `with` statement is used to indicated when code runs in a special context, i.e. mutual-exclusion locks can be used in `with` statement to indicated that this code runs only while the lock is held:
```py
from threading import Lock


lock = Lock()

with lock:
    # do something while maintaining invariant
```

This is equivalent to `try/finally` construction:
```py
lock.acquire()
try:
    # do something while maintaining invariant
finally:
    lock.release()
```
`with` statements if a handy tool ro remove repetitive blocks of code and not to forget to something to close or release or clean up. 

It is easy to make your objects and functions to work with `with` statement by using `contextlib.contextmanager` decorator.

For example temporary change debug lvl:
```py
import logging


def my_function():
    logging.debug(" * Debug data")
    logging.error(" * Error data")
    logging.debug(" * More debug data")
```
Default log level is INFO, so the only error data will be logged.
```py
my_function()
```
    >>>
    ERROR:root: * Error data

Here we can change log level quickly and restore it back with no effort:
```py
@contextmanager
def debug_logging(level):
    old_level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(level)
    try:
        yield
    finally:
        logging.getLogger().setLevel(old_level)

with debug_logging(logging.DEBUG):
    print(" * Inside")
    my_function()

print(" * Outside")
my_function()
```
    >>>
     * Inside
    DEBUG:root: * Debug data
    ERROR:root: * Error data
    DEBUG:root: * More debug data
    * Outside
    ERROR:root: * Error data

### Using `with` Targets
The context manager passed to a `with` statement can also return object, this object is assigned to the local variable in the `as` part of the `with` statement. This gives you an ability to directly interact with context manager. 

Common example is interaction with files:
```py
with open("data.json", "w") as f:
    f.write("Data to be written to the file")
```
To enable this functionality in your logger example we need change `yield` part:
```py
import sys
import logging
from contextlib import contextmanager


logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)
```
Calling logging methods like `DEBUG` on the `as` target produces output because the logging severity level is low enough in the `with` block on that specific logger instance. Using the `logging` module directly won't print anything because the global severity level is set to `WARNING`.
```py
with log_level(logging.DEBUG, "my_log") as logger:
    logger.debug(f" * This is a message for {logger.name}!")
    logging.debug("This will not print")
```
    >>>
    DEBUG:my_log: * This is a message for my_log!

However, calling `logging` directly will not print the message:
```py
logger = logging.getLogger("my_log")
logger.debug("Debug will not print")
logger.error("Error will print")
```
    >>>
    ERROR:my_log:Error will print

Also, renaming of the logger is also made easy:
```py 
with log_level(logging.DEBUG, 'other-log') as logger:
    logger.debug(f'This is a message for {logger.name}!')
    logging.debug('This will not print')
```
    >>>
    DEBUG:other-log:This is a message for other-log!


## Item 67: Use `datetime` Instead of `time` for Local Clock

    
# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
