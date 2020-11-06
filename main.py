class NoNewData(Exception):
    pass


def readline(handle):
    offset = handle.tell()
    handle.seek(0, 2)
    length = handle.tell()
    
    if length == offset:
        raise NoNewData
    
    handle.seek(offset, 0)
    return handle.readline()


import time


def tail_file(handle, interval, write_func):
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(intervale)
        else:
            write_func(line)


from threading import Lock, Thread


def run_threads(handles, interval, output_path):
    with open(output_path, "wb") as output:
        lock = Lock()
        def write(date):
            with Lock:
                output.write(date)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread =Thread(target=tail_file, args=args)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    print("hello world")
