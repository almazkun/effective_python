# Chapter 7. Concurrency and Parallelism

***Concurrency*** enables a computer to do many different things ***seemingly*** at the same time. For example, operating system on a single CPU computer rapidly changes which program is running. In doing so, it interleaves execution of the program, providing the illusion that the programs are running simultaneously.

***Parallelism***, on the other hand, involves ***actually*** doing many different things at the same time. A computer with multiple CPUs can execute multiple programs simultaneously. Each CPU running instructions of different programs, allowing computational progress during the same instance.

Within a single program, concurrency is a tool to make it easier to solve certain types of problems. Concurrent programs enable many distinct paths of execution, including separate streams of I/O, to make forward process in a way that seems to be both simultaneous and independent.

The key difference between *concurrency* and *parallelism* is ***speedup***. When two distinct paths of execution of the program make forward progress in parallel, the time it takes to do the total work is cut by *half*; speed of execution is faster by factor of two. In contrast, concurrent programs may run thousands of separate paths of execution seemingly in parallel bu provide no speed for total work. 

Python provides variety of ways to write a concurrent program. Threads support relatively small amount of concurrency, when coroutines enables a vast number of concurrent functions. Python also enables to do parallel works through system calls, subprocesses, and C extension. But it can be very difficult to make concurrent Python code truly run in parallel. It is important to understand how to best utilize Python in these different situations.

## Item 52: Use `subprocess` to Manage Child Process

Python is grate and has many ways to run subprocesses, and the best choice for managing child processes is to use the `subprocess` built-in module. For example, here is a function to start a process, read its output, and verify that it terminated cleanly:
```python
import os
import subprocess


os.environ["COMSPEC"] = "powershell"

result = subprocess.run(
    ["Write-Host", "Hello from the child"],
    capture_output=True,
    encoding="utf-8",
    shell=True)

result.check_returncode() # No exception means clean exit
print(result.stdout)
```
    >>>
    Hello from the child

* Child processes run independently from their parent process, the Python interpreter. If we use `popen` to create a subprocess, we can periodically poll child process status:
```python
proc = subprocess.Popen(["sleep", "1"], shell=True)
while proc.poll() is None:
    print("Working...")
    import time
    time.sleep(0.4)

print("Exit status", proc.poll())
```
    >>>
    Working...
    Working...
    Working...
    Working...
    Exit status 0

* Decoupling the child process from the parent frees up the parent process to run child processes in parallel. Here, we do this by starting all the child processes together with `Popen` upfront:
```python
import time


start = time.time()
sleep_procs = []
for _ in range(10):
    proc = subprocess.Popen(["sleep", "1"], shell=True)
    sleep_procs.append(proc)
```
Later, we wait them to finish their I/O and terminate with `communicate` method:
```python
for proc in sleep_procs:
    proc.communicate

end = time.time()
delta = end - start

print(f"Finished in {delta:.3} seconds")
```
    >>>
    Finished in 2.09 seconds

If these processes run in sequence, the total delay would be 10 seconds and more, not ~ 2 seconds.

* We can also pipe data from Python program into a subprocess and retrieve its output.This allows us to utilize many program to run in parallel.For example, we want to encrypt our data with `openssl`. Starting the child process with commend-line argument and I/O pipe is easy:
```python
import os


def run_encrypt(data):
    env = os.environ.copy()
    env["password"] = "4(;QlJ?mVXv?^|+q@UmR%eQaq|Aqh):?"
    proc = subprocess.Popen(
        ["openssl", "enc", "-des3", "-pass", "env:password"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    proc.stdin.write(data)
    proc.stdin.flush() # Ensure that the child gets input
    return proc
```
Here we encrypt random numbers
```python
procs = []
for _ in range(3):
    data = os.urandom(10)
    proc = run_encrypt(data)
    procs.append(proc)
```
The child processes run in parallel and consume their input, and retrieve their final output:
```python
for proc in procs:
    out, _ = proc.communicate()
    print(out[-10:])
```
    >>>
    b'\x96\x82\x82\x9e\xde\xfa\x90\xe21t'
    b'&\nRG\xab\x04\x99\xd7\xc1"'
    b'x\xe3\xb8\xb8\xd7\xe5t\x03@\x8e'
* It is also possible to create a chain of parallel processes, connecting the output of one child process to the input of another, and so on. Here is the command-line tool to output Whirlpool hash of the input stream:
```python
def run_hash(input_stdin):
    return subprocess.Popen(
        ["openssl", "dgst", "-whirlpool", "-binary"],
        stdin=input_stdin,
        stdout=subprocess.PIPE)
```
Now we can create set of processes to encrypt some data and hash the output:
```python
encrypt_procs = []
hash_procs = []

for _ in range(3):
    data = os.urandom(100)
    encrypt_proc = run_encrypt(data)
    encrypt_procs.append(encrypt_proc)
    hash_proc = run_hash(encrypt_proc.stdout)
    hash_procs.append(hash_proc)
    # Ensure that the child consumes the input stream and 
    # the communicate() method doesn't inadvertently steal
    # input from the child. Also lets SIGPIPE propagate to 
    # upstream process if the downstream process dies.
    encrypt_proc.stdout.close()
    encrypt_proc.stdout = None
```
THe I/O between the child processes happens automatically once they are started:
```python
for proc in encrypt_procs:
    proc.communicate()
    assert proc.returncode == 0

for proc in hash_procs:
    out, _ = proc.communicate()
    print(out[-10:])
    assert proc.returncode == 0
```
    >>>
    b'\xe5{.\x8fu\xa5\x06\x9d@P'
    b'\xd8\xce\xba\x84\x9d\xcf\xc5\xfe\x86\x95'
    b'[\x02\x9a\xb5M\x0e\xbd\x99)\x86'

* If we worry that child process never terminate or somehow blocking on input or output pipes, we can use `timeout` parameter to the `communicate` method. THis causes an exception to be raised of the process hasn't finished in time:
```python
proc = subprocess.Popen(['sleep', '10'], shell=True)

try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()

print('Exit status', proc.poll())
```
    >>>
    Exit status 1

## Item 53: Use Treads for Blocking I/O, Avoid Parallelism

The standard implementation of Python called CPython. CPython runs a Python program in two steps. First, it parses and compiles the source text into `bytecode`, which is low-level representation of the program as 8-bit instructions. Then, CPython runs bytecode using stack-based interpreter. The bytecode interpreter has state that must be maintained and coherent while Python program executes. CPython enforces the coherence with a mechanism called `global interpreter lock` (GIL).

Essentially, the GIL is a mutual-execution lock (mutex) that prevents CPython being affected by preemptive multithreading, where one thread takes control of a program by interrupting another thread. Such an interruption could corrupt the interpreter state (e.g. garbage collection reference count) if it comes at an unexpected time. The GIL prevents these interruptions and ensures that every bytecode instruction work correctly with the CPython implementation and its C-extension modules. 

THe GIL has an important negative side effect. With programs written in languages like `C++` or `Java`, having multiple threads of execution means that a program can utilize multiple CPU cores at the same time. Although Python supports multiple threads of execution, GIL causes only one of them to be executed at a time. WHich mean that when you reach for threads for parallel computation and speed up your Python program, yu will be sorely disappointed.

* For example, we need to do something computationally intensive in Python, like number factorization algorithm:
```python
def factorize(number):
    for i in range(1, number + 1):
        if number % i ==0:
            yield i
```
Factoring a set of numbers would take sometime:
```python
import time 


numbers = [2139079, 1214759, 1516637, 1852285]
start = time.time()


for number in numbers:
    list(factorize(number))

end = time.time()
delta = end - start
print(f"Took {delta:.3} seconds")


```
    >>>
    Took 0.756 seconds

* Using multiple threads to do this would make sense. Let's us try to implement it:
```python
from threading import Thread


class FactorizeThread(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number
    def run(self):
        self.factors = list(factorize(self.number))
```
Then, we start start a thread for each number to factorize in parallel:
```python
start = time.time()


threads = []
for number in numbers:
    thread = FactorizeThread(number)
    thread.start()
    threads.append(thread)


```
We wait them to calculate and print the result:
```python
for thread in threads:
    thread.join()


end = time.time()
delta = end - start
print(f"Took {delta:.3} seconds")
```
    >>>
    Took 1.16 seconds

As we can see it took even longer to do the same calculations. Here we can see effect of the GIL on a program running on standard CPython interpreter.

* However there are way for CPython utilize multiple cores. But the standard `Thread` class do not work with multiple threads. ALso, implementing implementing multiple thread computation may require substantial effort. Given these limitation, why does Python supports threads at all? There are two good reasons.

First, multiple threads make it easy for a program to seem like it's doing multiple things at the same time. Managing the juggling act of simultaneous tasks is difficult to implement yourself. With threads Python will take care of your concurrently running functions. THe CPython will ensure fairness between Python threads of execution, even though only one of them faking further progress at a time.

Second reason, THreads used to deal with blocking I/O, which happens when Python does certain types of system calls.

* Python programs use system calls to ask the computer's operating system to interact with the external environment on its behalf. Blocking I/O includes things like reading and writing files, interacting with networks, communicating with devices like displays, and so on. Threads help handle blocking I/O by insulating a program from the time it takes for the operating system to response to requests.

For, example we need to send signal to remote-controlled helicopter through a serial port. We use s slow system call (`select`) as a proxy for that activity. THis function asks the operating system to block for 0.1 second and return control to my program, which is similar to what would happen when using a synchronous serial port:
```python
import select
import socket


def slow_systemcall():
    select.select([socket.socket()], [], [], 0.1)

```
Running this system call in serial requires a linear increasing amount of time:
```python
start = time.time()

for _ in range(5):
    slow_systemcall()

end = time.time()
delta = end - start
print(f"Took {delta:.3f} seconds")
```
    >>>
    Took 0.654 seconds

* The problem is that while the `slow_systemcall` function is running, my program can't make any other progress. My program's main thread of execution is blocked on the `select` system call. This situation is awful in practice. You need to be able to compute your helicopter's next move while you are sending it a signal, otherwise, it will crash. This is when `Threads` will help us.

Here we can run multiple `slow_systemcall` functions in separate threads. THis will allow to compute other tasks while leaving main thread to do its job.
```python

#```
#With the threads started, here we do calculations of the next move, before waiting for the system call thread to finish:
#```python

threads = []

for _ in range(5):
    thread = Thread(target=slow_systemcall)
    thread.start()
    threads.append(thread)


def compute_helicopter_location(index):
    pass

start = time.time()
for i in range(5):
    compute_helicopter_location(i)

for thread in threads:
    thread.join()

end = time.time()
delta = end - start
print(f"Took {delta:.3f} seconds")
```
    >>>
    Took 0.306 seconds

This way we can show that all system calls will run in parallel from multiple Python threads, even though they are limited by GIL. 

We can deal with blocking I/O also using `asyncio` build-in module and these alternative have important benefits, but those options might require extra work.

## Item 54: Use `Look` to Prevent Data Races in Threads

After reading about GIL, many new Python programmers assume they can forgo using mutual-exclusion locks (also called mutexes) in their code altogether. The GIL already preventing python threads running on multiple CPU cores in parallel, it also should lock the program's data. On some lists and dicts it seems like true. 

But beware, GIL will not protect you. Even though, only one tread runs at a time, a thread's operations on data structures may be interrupted between any two bytecode instructions. This is dangerous if you access the same object from multiple threads simultaneously. This may lead to the invariants of data structures and leaving a program in a corrupted state. 

* For example, we need a program that counts many things in parallel, like sampling a light level from whole network of sensors. If we need to know total number of samples over time, we can aggregate them with a new class:
```python
class Counter:
    def __init__(self):
        self.count = 0

    
    def increment(self, offset):
        self.count += offset
```
Each sensor should have its own worker thread because reading from the sensor requires blocking I/O. After each sensor measurement, the worker thread increments the counter up to the maximum number of desired threads. 
```python
def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        # Read from the sensor
        ...
        counter.increment(1)
```
Now, we will run worker thread for each sensor in parallel:
```python
from threading import Thread


how_many = 10**5
counter = Counter()


threads = []
for i in range(5):
    thread = Thread(target=worker, args=(i, how_many, counter))
    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()


expected = how_many*5
found = counter.count
print(f"Counter should be {expected}, got {found}")
```
    >>>
    Counter should be 500000, got 285627

Why is this happened? Problem is that Python interpreter enforces fairness between all of the threads that are executing to ensure they are getting roughly equal processing time. To do so, Python suspends a thread as it running and resumes another thread in turn. But you may not know exactly when will Python do that. That's what happened it this case.

The body of the `Counter` object's `increment` method looks simple, and for a worker it looks like this:
```python
counter.count += 1
```
But the += operation used on the object looks for the Python interpreter this way:
```python
value = getattr(counter, "count")
result = value + 1
setattr(counter, "count", result)
```
Python threads incrementing the counter can be interrupted between any of this operations. This is problematic because the wrong value can be incremented:
```python
# Running in Thread A 
value_a = getattr(counter, "count")
# Context switch to Tread B
value_b = getattr(counter, "count")
result_b = value_b +1
setattr(counter, "count", result_b)
# Context switch to back to Tread A
context_a = value_a + 1
setattr(counter, "count", result_a)
```
Thread B interrupted Thread A in the middle of calculation and finished, then tread A continued, overwriting all of the progress made in Thread B in incrementing the counter. This is exactly what happened in the example above with the light sensors. 

To prevent date races like this and other forms of data structure corruption, Python has robust set of tools in `threading` built-in module. The simplest and most useful is `Lock` class, a mutual-exclusion lock (mutex).

Here is the `Counter` class protected against simultaneous access. Only one thread will be able to acquire lock at a time. Here is `with` is used to acquire and release the lock:
```python
from threading import Lock


class LockingCounter:
    def __init__(self):
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:
            self.count += offset
```
Now we run `worker' thread with 'LockingCounter':
```python
counter = LockingCounter()

for i in range(5):
    thread = Thread(target=worker, args=(i, how_many, counter))
    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()

expected = how_many * 5
found = counter.count
print(f"Counter should be {expected}, got {found}")
```
    >>>
    Counter should be 500000, got 500000

`Lock` Solved the problem.

## Item 55: Use `Queue` to Coordinate Work Between Threads
To coordinate concurrent work in Python program it is very useful to use a pipeline of functions. 

A pipeline looks like a assembly line, it has mane phases in serial, with specific function for each serial. New pieces of work continuously added to the beginning of the pipeline. The functions can operate concurrently, each working on the piece of work in its phase. The work moves forward as each function completes until there is no phases remaining. This is very good approach for blocking I/O or subprocesses.

For example, we need a program which will take a constant stream of images from a camera, resize them and post them to the online photo gallery. Such program can be split into three phases: 1. New image retrieved from a camera; 2. Resized; 3 Uploaded. 

Let's assume that the functions `download`, `resize` and `upload` are already written:
```python
def download(item):
    return print(item, "downloaded.")


def resize(item):
    return print(item, "resized.")


def uploaded(item):
    return print(item, "uploaded.")
```
The first thing we need to do is design the way to hand a work from phase to phase. We can do it by using a thread-safe producer-consumer queue:
```python
from collection import deque
from threading import Lock


class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()
```
The Producer appends images to the end of the `deque`:
```python
    def put(self, item):
        with self.lock:
            self.items.append(item)
```
The consumer removes images from the front of the `deque`:
```python
    def get(self):
        with self.lock:
            return self.items.popleft()
```
Now we represent each phase of the pipeline as a Python thread that takes work from one queue, runs a function, and puts result in another queue. It also counts how many time the worker has checked for new input and how much work isn't completed:
```python
from threading import Thread
import time
    
   
class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0
```
The trickiest part is that the worker thread need sto properly handle the situation where the input queue is empty because the previous phase isn't finished yet. It is implemented in the section where `IndexError` catch is, it is like a holdup in assembly line. 
```python
    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01) # No work to do
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1
```
Now we can connect the three phases together by creating the queues for their coordination points and corresponding worker threads:
```python
download_queue = MyQueue()
resize_queue = MyQueue()
upload_queue = MyQueue()
done_queue = MyQueue()
threads = [
    Worker(download, download_queue, resize_queue),
    Worker(resize, resize_queue, upload_queue),
    Worker(upload, upload_queue, done_queue),
]
```
Now we can start the thread and inject the work in it:
```python
for thread in threads:
    thread.start()


for _ in range(1000):
    download_queue.put(object())
```
Now we wait until all work end up in `done_queue`:
```python
while len(done_queue.items) < 1000:
    pass
```
This runs properly, but has an interesting side effect. The part where we catch `IndexError` exception in the `run` method, executes a large number of times:
```python
processed = len(done_queue.items)
polled = sum(t.polled_count for t in threads)
print(f"Processed {processed} items after polling {polled} times")
```
    >>>
    Processed 1000 items after polling 3662 times

When the worker functions vary in their respective speeds, an earlier phase can prevent progress in the later phases, backing up the pipeline. This causes the later processes to starve and constantly check their input quest, which is waisting CPU time doing nothing. 

Three are also a three more problems with this implementation. First, determining that all of the input work is complete requires yet another busy wait on the `done_queue`. Second, in `Worker`, the `run` method will execute forever in its busy loop, there is no obvious way to signal to a worker thread that it's time to exit. Third, worst of all, it can cause the program to crash, because the program will eventually run out of memory. 

It is hard to write good producer-consumer queue yourself. So why even bother?

* `Queue` to the Rescue

The Queue class from `queue` build-in modules provide all of the functionality you need to solve these problems. 

`Queue` eliminates  the busy waiting in the worker by making the `get` method block until new data comes in.
```python
from queue import Queue


my_queue = Queue()


def consumer():
    print("Consumer waiting")
    my_queue.get()              # Runs after put() below
    print("Consumer done")


thread = Thread(target=consumer)
thread.start()
```
Even though the thread is running first, it won't finish until an item is `put()` on the `Queue` instance and `get()` has something to return.
```python
print("Producer putting")
my_queue.put(object())          # Runs before get() above
print("Producer done")
thread.join()
```
    >>>
    Consumer waiting
    Producer putting
    Producer done
    Consumer done
To solve the pipeline backup issue, the Queue class allows to specify the maximum amount of pending work allowed between two phases.

This buffer size blocks `put` when the queue is already full:
```python
my_queue = Queue(1)             # Buffer size of one


def consumer():
    time.sleep(0.1)             # Wait
    my_queue.get()              # Runs second
    print("Consumer got 1")
    my_queue.get()              # Runs fourth
    print("Consumer got 2")
    print("Consumer done")


thread = Thread(target=consumer)
thread.start()
```
The wait should allow the producer thread to put both objects on the queue before the consumer thread even calls get. But, the size of `Queue` is one. This mean that producer have to wait at one get call from a consumer before being able to add a new item:
```python
my_queue.put(object())          # Runs first
print("Producer put 1")
my_queue.put(object())          # Runs third
print("Producer put 2")
print("Producer done")
thread.join()
```
    >>>
    Producer put 1
    Consumer got 1
    Producer put 2
    Producer done
    Consumer got 2
    Consumer done
* The `Queue` class can also track the progress of work using `task_done` method. 
Here is the example of `consumer` method using `task_done` when it finishes working on the item. 
```python
in_queue = Queue()
def consumer():
    print("Consumer waiting")
    work = in_queue.get()       # Runs second
    print("Consumer working")
    # Working
    ...
    print("Consumer done")
    in_queue.task_done()        # Runs third


thread = Thread(target=consumer)
thread.start
```
Now, producer code doesn't have to join the consumer thread or poll. Producer can just wait for the `in_queue` to finish by calling `join` on `Queue` instance. Even once it's empty, the `in_queue` won't be joinable until after `task_done` is called for every item that was ever enqueued:
```python
print("Producer putting")
in_queue.put(object())
print("Producer waiting")
in_queue.join()
print("Producer done")
thread.join()
```
    >>>
    Consumer waiting
    Producer putting
    Producer waiting
    Consumer working
    Consumer done
    Producer done

* We can put all these behavior into a `Queue` subclass that also tells the worker thread when it should stop processing. 
We can accomplish it by defining special `close method` that adds a special `sentinel` item to the queue that indicated that there will be no more input after it.
```python
class ClosableQueue(Queue): 
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)
```
Then, we add iterator for the queue, that looks for special object and stops iteration when it's found. This `__iter__` method also calls `task_done`at appropriate times, letting me track the progress of work in the queue.
```python
    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return # Cause the thread to exit
                yield item
            finally:
                self.task_done()
```
Now, we can redefine the worker thread to rely on the behavior of the `ClosableQueue` class. The thread will exit when the for loop is exhausted.
```python
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)
```
Re-write the set of worker threads with new worker class:
```python
download_queue = ClosableQueue()
resize_queue = ClosableQueue()
upload_queue = ClosableQueue()
done_queue = ClosableQueue()
threads = [
    StoppableWorker(download, download_queue, resize_queue),
    StoppableWorker(resize, resize_queue, upload_queue),
    StoppableWorker(upload, upload_queue, done_queue),
]
```
After running this worker thread we will also send the stop signal by closing the input queue of the first phase:
```python
for thread in threads:
    thread.start()

for _ in range(1000):
    download_queue.put(object())

download_queue.close()
```
Finally, we wait for the work to finish by joining the queues that connect the phases:
```python
download_queue.join()
resize_queue.close()
resize_queue.join()
upload_queue.close()
upload_queue.join()
print(done_queue.qsize(), "items finished")

for thead in threads:
    thread.join()
```
    >>>
    1000 items finished

* We can also make multiple worker threads for each phase. 
This way we can increase I/O parallelism and speed up these types of program significantly. For that we need to define a helper function which will stop and start each parallel thread.
```python
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


def stop_threads(closable_queue, threads):
    for _ in threads:
        closable_queue.close()

    closable_queue.join()

    for thread in threads:
        threads.join()
```
Putting everything together:
```python
download_queue = ClosableQueue()
resize_queue = ClosableQueue()
upload_queue = ClosableQueue()
done_queue = ClosableQueue()

download_threads = start_threads(3, download, download_queue, resize_queue)
resize_threads = start_threads(4, resize, resize_queue, upload_queue)
upload_threads = start_threads(5, upload, upload_queue, done_queue)

for _in range(1000):
    download_queue.put(object())

stop_threads(download_queue, download_threads)
stop_threads(resize_queue, resize_threads)
stop_threads(upload_queue, upload_threads)

print(done_queue.qsize(), "items finished")
```
    >>>
    1000 items finished


`Queue` class is great for building robust pipelines.


# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)