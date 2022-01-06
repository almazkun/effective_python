def try_finally_example(filename):
    print(" * Open file")
    handle = open(filename, encoding='utf-8') # OSError may happen
    try:
        print(" * Read file")
        return handle.read() # UnicodeDecodeError may happen
    finally:
        print(" * Close file")
        handle.close() # Always executed after `try` block

if __name__ == "__main__":
    try_finally_example('does_not_exist.txt')
