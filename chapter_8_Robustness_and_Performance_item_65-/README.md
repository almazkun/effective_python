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

#### `else` block

# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)
