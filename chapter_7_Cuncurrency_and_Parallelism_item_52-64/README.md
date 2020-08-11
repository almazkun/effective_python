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


## Item 56:Know How to Recognize When Concurrency is Necessary
Here is an implementation of the Conway's Game of Life, a finite state automata illustration. THe rules a explained below. It start with 2-dimensional grid, of arbitrary size, with cells either Alive ` * ` or Dead ` - `. Based of the state of the neighboring sells on each turn each cell decides if its Alive, Dead or should regenerate. 
* This is the representation of the game 5*5 grid after 4 generations:

0|1|2|3|4
-|-|-|-|-
----- | ----- | ----- | ----- | -----
-*--- | --*-- | --**- | --*-- | -----
--**- | --**- | -*--- | -*--- | -**--
---*- | --**- | --**- | --*-- | -----
----- | ----- | ----- | ----- | -----

* We can represent the state with simple container class:
```python
EMPTY = "-"
ALIVE = "*"
class Grid:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)
        
    def get(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def set(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state
    
    def __str__(self):
        output = ''
        for row in self.rows:
            for cell in row:
                output += cell
            output += '\n'
        return output
```
We can see the result of the class:
```python
grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)
```
    >>>
    ---*-----
    ----*----
    --***----
    ---------
    ---------

* Here is a helper function, to retrieve information about living neighbors:
```python
def count_neighbors(y, x, get):
    n_ = get(y - 1, x + 0) # North
    ne = get(y - 1, x + 1) # Northeast
    e_ = get(y + 0, x + 1) # East
    se = get(y + 1, x + 1) # Southeast
    s_ = get(y + 1, x + 0) # South
    sw = get(y + 1, x - 1) # Southwest
    w_ = get(y + 0, x - 1) # West
    nw = get(y - 1, x - 1) # Northwest
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0

    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    return count
```
* Now we define `game_logic`, the rule is: Become alive if 3 neighbors are `ALIVE`. die if 2 or less and 4 or more:
```python
def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY        # Die if less than 2
        elif neighbors > 3:
            return EMPTY        # Die if more that 3 
    else:
        if neighbors == 3:
            return ALIVE        # Regenerate
    return state
```
* Next function will change the state of the grid, check the state of cell, inspect the states of neighbors and update the resulting grid accordingly:
```python
def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)
```
* Finally, we define function that will move forward the game, calling the `get` method on previous version of the grid and calling `set` method on the next version of the grid:
```python
def simulate(grid):
    next_grid = Grid(grid.height, grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid
```
* Now? we can progress the game one stem at the time:
```python
class ColumnPrinter:
    def __init__(self):
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        for data in self.columns:
            row_count = max(
                row_count, len(data.splitlines()) + 1)

        rows = [''] * row_count
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    padding = ' ' * (len(line) // 2)
                    rows[j] += padding + str(i) + padding
                else:
                    rows[j] += line

                if (i + 1) < len(self.columns):
                    rows[j] += ' | '

        return '\n'.join(rows)


columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate(grid)

print(columns)
```
    >>>
        0     |     1     |     2     |     3     |     4    
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

THis approach is working great for running in one thread on one machine. But is the requirements were to change to make possible I/O in `game_logic` to make it online game, where the transition of state is dependant in grid state and the communication with the other players over the internet. 

The simplest approach would be to add blocking I/O directly to the `game_logic`:
```python
def game_logic(state, neighbors):
    ...
    # Do some blocking input/output in here:
    date = my_socket.recv(100)
    ...
```
The problem with this approach, that it will slow down the program. If we consider the latency of 100 milliseconds and a grid of 45 cells it will take 4,5 seconds for a one turn. Also, it scales poorly, for a grid of 10000 cells it would need over 15 minutes to evaluate each generation.

The solution is to do I/O in parallel so each generation takes roughly 100 milliseconds, regardless of the grid size. The process of `spawning` a concurrent line of execution for each unit of work is called `fan-out`. Waiting for all the those concurrent units to finish before moving to the net phase in a coordinated process is called `fan-in`.

Python provides many tools for achieving `fan-out` and `fan-in`. Which will be covered in the next chapters.

## Item 57: Avoid Creating New `Thread` Instance for On-demand Fan-out:
`Threads` are natural first tool to reach for doing parallel I/O in Python. However, they have significant down side when you apply them for fanning-out too many concurrent lines of execution. 

To demonstrate it we will use our implementation of `Game of Life`, where we will use threads to sole the latency problem caused by doing I/O in the `game_logic` function.

* To begin with, threads require coordination using Lock to ensure that concurrent usage won't damage data structures. We can create a subclass of a `Grid` class to add locking behavior:
```python
from threading import Lock


class LockingGrid(Grid):
    def __init__(self, height, width):
        super().__init__(height, width)
        self.lock = Lock()

    def __str__(self):
        with self.lock:
            return super().__str__()
    
    def get(self, y, x):
        with self.lock:
            return super().get(y, x)
    
    def set(self, y, x, state):
        with self.lock:
            return super().set(y, x, state)

```
* Then, we can rewrite `simulate` function to *fan-out* by creating a thread for each call to `step_cell`. The Threads will run in parallel. Then we will `fan-in` by waiting for all of the calls complete before moving to the next generation.
```python
from threading import Thread


def count_neighbors(y, x, get):
    ...

def game_logic(state, neighbors):
    ...
    # Do some blocking/ I/O in here:
    data = my_socket.recv(100)
    ...

def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)

def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)


def simulate_threaded(grid):
    next_grid = LockingGrid(grid.height, grid.width)

    threads = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            thread = Thread(target=step_cell, args=args)
            thread.start()                                  # Fan-out
            threads.append(thread)
    
    for thread in threads:
        thread.join()                                       # Fan-in

    return next_grid
```
We can run this code with the same `step_cell` and the sane driver with only two lines changed:
```python
grid = LockingGrid(5 , 9)

grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate_threaded((grid)

print(columns)
```
    >>>
        0     |     1     |     2     |     3     |     4    
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

* This works as expected. However this code has three big problems:

    - The `Thread` instance require special coordinator, this makes threaded code harder extend and maintain over time.
    - Threads require a lot of memory - about 8 MB per thread - which will be a problem when number of threads grow. 
    - Starting a thread is costly, whish lead to negative performance impact when they run and switch between each other. 

* This code also is difficult to debug. For example `game_logic` rises and exception, whish is highly likely due to the nature of I/O:
```python
def game_logic(state, neighbors):
    ...
    raise OSError("Problem with I/O")
    ...
```
We can test this by pointing `sys.stderr` output to the in-memory `StringIO` buffer:
```python
import contextlib
import io


fake_stderr = io.StringIO()
with contextlib.redirect_stderr(fake_stderr):
    thread = Thread(target=game_logic, args=(ALIVE, 3))
    thread.start()
    thread.join()

print(fake_stderr.getvalue())
```
    >>>
    Exception in thread Thread-1520646:
    Traceback (most recent call last):
        File "C:\Users\Home\Anaconda3\lib\threading.py", line 926, in _bootstrap_inner
            self.run()
        File "C:\Users\Home\Anaconda3\lib\threading.py", line 870, in run
            self._target(*self._args, **self._kwargs)
        File "<ipython-input-15-526c19a86b48>", line 2, in game_logic
            raise OSError("Problem with I/O")
    OSError: Problem with I/O

An exception is raised as expected, however the code created the `thread` and called `.join()` on it is unaffected. This happens because the `Thread` class will catch all the exceptions raised by target function. 

Thus, this makes `Threads` not the best solution for on-demand threading.


## Item 58: Understand How Using `Queue` for Concurrency Requires Refactoring
To avoid problems with `Threads`, we can use `Queues`. We can define a fixed number of workers threads upfront. This will minimize the threading overhead and allow parallelism. 

* To so this, we two `ClosableQueue` instances to use for communicating to and from the worker threads that execute `game_logic` function.
```python
from queue import Queue

class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return  # Cause the thread to exit
                yield item
            finally:
                self.task_done()


in_queue = ClosableQueue()
out_queue = ClosableQueue()
```
* We can start multiple threads that will consume items from the `in_queue`, process them by calling `game_logic`, and put the results in `out_queue`. These threads will run concurrently, allowing for the parallel I/O.

```python
class StoppableWorker(Thread):
    ...


def game_logic(state, neighbors):
    ...
    # Some blocking I/O
    data = my_socket.recv(100)
    ...


def game_logic_thread(item):
    y, x, state, neighbors = item
    try:
        next_state = game_logic(state, neighbors)
    except Exception as e:
        next_state = e
    return y, x, next_state


# Start the thread upfront
threads = []
for _ in range(5):
    thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
    thread.start()
    threads.append(thread)
```
* Now, redefine the `simulate` function to interact with these queues. Adding item to `in_queue` is *fan-out* and emptying `out_queue` is *fan-in*.
```python
ALIVE = "*"
EMPTY = "_"


class SimulationError(Exception):
    pass


class Grid:
    ...


def count_neighbors(y, x, get):
    ...


def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            neighbors = count_neighbors(y, x, grid.get)
            in_queue.put((y, x, state, neighbors)) # Fan out

    in_queue.join()
    out_queue.close()

    next_grid = Grid(grid.height, grid.width)
    for item in out_queue:
        y, x, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)
    
    return next_grid
```
The call to `grid.get` and `grid.set` both happen in `simulate_pipeline` function, which mean we can use single threaded implementation of a `Grid` class.

* This code is also easier to debug, because it will catch an exception in the `game_logic` function and raised in the main thread:
```python
def game_logic(state, neighbors):
    raise OSError("Problem with I/O in game_logic")


simulate_pipeline(Grid(1, 1), in_queue, out_queue)
```
    >>>
    Traceback (most recent call last)
    OSError: Problem with I/O in game_logic
    SimulationError: (0, 0)

* We can drive this multithreaded pipeline by calling `simulate_pipeline` in a loop:
```python
class ColumnPrinter:
    ...

grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5)
    columns.append(str(grid))
    grid = simulate_pipeline(grid, in_queue, out_queue)

print(columns)

for thread in threads:
    in_queue.close()
for thread in threads:
    thread.join()
```
    >>>
        0     |     1     |     2     |     3     |     4    
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

THe result is the same, we solved the memory problem, but other problems remain:
    - `simulated_pipeline` is even harder to follow than `simulated_threaded` approach.
    - Extra support classes `ClosableQueue` and `StoppableWorker` add complexity.
    - Have to specify number of threads upfront, instead of the system automatically scaling as needed.
    - To catch an exception, you need to manually catch them in worker treads, and re-raise them in main thread.

However, the biggest problem is apparent if we need to additional parallelism. For instance, in `count_neighbors` function:
```python
def count_neighbors(x, y, state):
    # Some blocking I/O is here
    data = my_socket.recv(100)
```
* In order to make it parallelizable we need to add another step to the pipeline that runs it in a thread. We need to make sure that exception will propagate to main thread and we need to use `Lock` in `Grid` to ensure correct synchronization between worker threads. 
```python
def count_neighbors_thread(item):
    y, x, state, get = item
    try:
        neighbors = count_neighbors(y, x, get)
    except Exception as e:
        neighbors = e
    return y, x, state, neighbors


def game_logic_thread(item):
    y, x, state, neighbors = item
    if isinstance(neighbors, Exception):
        next_state = neighbors
    else:
        try:
            next_state = game_logic(state, neighbors)
        except Exception as e:
            next_state = e
    return y, x, next_state


class = LockingGrid(Grid):
    ...
```
* Also, we need to create new set of `Queue` instances for the `count_neighbors_thread` workers and the corresponding `Thread` instances:
```python
in_queue = ClosableQueue()
logic_queue = ClosableQueue()
out_queue = ClosableQueue()


threads = []

for _ in range(5):
    thread = StoppableWorker(
        count_neighbors_thread, in_queue, logic_queue)
    thread.start()
    threads.append(thread)


for _ in range(5):
    thread = StoppableWorker(
        game_logic_thread, logic_queue, out_queue)
    thread.start()
    threads.append(thread)
```
* Finally, we need update `simulate_pipeline` to coordinate multiple phases in the pipeline and ensure that work fans out and back correctly:
```python
def simulate_phased_pipeline(
        grid, in_queue, logic_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            item = (y, x, state, grid.get)
            in_queue.put(item) # Fan out
    
    in_queue.join()
    logic_queue.join()
    out_queue.close()

    next_grid = LockingGrid(grid.height, grid.width)
    for item in out_queue:
        y, x, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)
    
    return next_grid
```
Now it is possible to run multiple phase pipeline:
```python
grid = LockingGrid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate_phased_pipeline(
            grid, in_queue, logic_queue, out_queue)

print(columns)

for thread in threads:
    in_queue.close()
for thread in threads:
    logic_queue.close()
for thread in threads:
    out_queue.join()
```
    >>>
        0     |     1     |     2     |     3     |     4    
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | --*-*---- | ----*---- | ----*----
    --***---- | ---**---- | ---**---- | --*-*---- | --*-*----
    --------- | ---*----- | ---*----- | ---**---- | ---**----
    --------- | --------- | --------- | --------- | ---------

* This works, but requires a lot of change. `Queue` can solve fan out, fan in problems and better than `Threads` in this regards. But they are not ideal as other tools, like `ThreadPoolExecutor` form the next chapter.

## Item 59: Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency

Python provides `concurrent.futures` built-in module, where we can find `ThreadPoolExecutor` class. THis class combines best parts of the `Thread` and `Queue` for solving blocking I/O parallelisation.
```python
ALIVE = "*"
EMPTY = "_"

class Grid:
    ...


class LockingGrid(Grid):
    ...


def count_neighbors(y, x, get):
    ...


def game_logic(state, neighbors):
    ...
    # Do some blocking input/output in here:
    data = my_socket.recv(100)
    ...


def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = game_logic(state, neighbors)
    set(y, x, next_state)
```
* Instead of starting a new `Thread` instance for each `Grid` square, we can fan out by pushing a function to an executor, whish will run in separate thread. Later, after all calculations we will fan in:
```python
from concurrent.futures import ThreadPoolExecutor


def simulate_pool(pool, grid):
    next_grid = LockingGrid(grid.height, grid.width)

    futures = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            future = pool.submit(step_cell, *args) # Fan out
            futures.append(future)
    
    for future in futures:
        future.result()                            # Fan in

    return next_grid
```
The threads used for executor can be allocated in advance, the max amount of worker also can be specified with `max_workers` parameter:
```python
class ColumnPrinter:
    ...


grid = LockingGrid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
with ThreadPoolExecutor(max_workers=10) as pool:
    for i in range(5):
        columns.append(str(grid))
        grid = simulate_pool(pool, grid)

print(columns)
```
    >>>
        0     |     1     |     2     |     3     |     4    
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

* The best part of `ThreadPoolExecutor` is that Exception will propagate back to the caller:
```python
def game_logic(state, neighbors):
    raise OSError('Problem with I/O')

with ThreadPoolExecutor(max_workers=10) as pool:
    task = pool.submit(game_logic, ALIVE, 3)
    task.result()
```
    >>>
    Traceback (most recent call last)
      OSError: Problem with I/O

* If will need to add other parallel I/Os no modification to the program will be needed, because it is already doing it in parallel in `step_cell` function.

However, this can't be done for a big amount of parallel threads. It won't scale to 10000+ parallel threads.

## Item 60, Achieve Highly Concurrent I/O with Coroutines 

Python addresses the need of thousands concurrent I/Os with *coroutines*. Coroutines let you have a very large seemingly simultaneous functions in your Python program. They are implemented using `async` and `await` keywords along with the same infrastructure that powers generators. 

THe cost of a coroutine is a function call. An active coroutine uses less than 1KB of memory until it exhausted. Like threads, coroutines are independent functions that can consume an input and produce resulting output. THe coroutines pause at each `await` and continues at `async` function after pending awaitable is resolved (similar to how `yield` behaves).

Many separate `async` functions advanced in lockstep running simultaneously, mimicking the concurrent behavior of THreads. However the coroutines do it without memory overhead, startup and context switching costs, or complex locking and synchronization code that's required by Threads. The magic is done by the `event loop`, which can do highly concurrent I/Os efficiently.

* We can implement the coroutines in the Game of Life starting with `game_logic` function:
```python
ALIVE = "*"
EMPTY = "_"

class Grid:
    ...


class LockingGrid(Grid):
    ...


def count_neighbors(y, x, get):
    ...


async def game_logic(state, neighbors):
    ...
    # Do some blocking input/output in here:
    data = await my_socket.recv(100)
```
* Similarly, we turn `step_cell`function into coroutine:
```python
async def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = count_neighbors(y, x, get)
    next_state = await game_logic(state, neighbors)
    set(y, x, next_state)
```
* Also, `simulate` function is also needs to be a coroutine:
```python
import asyncio


async def simulate(grid):
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell(
                y, x, grid.set, next_grid.set)  # Fan out
            tasks.append(task)
        
    await asyncio.gather(*tasks)                # Fan in

    return next_grid
```
* Calling `step_cell` doesn't immediately run a function. Instead, it returns a coroutine instance that can be used with `await` expression later in time. This is similar to the `yield` returning a generator instance instead executing immediately. Deferring execution like this cause *fan-out*.
* The `gather` function from `asyncio` built-in cases *fan-in*. The `await` expression on `gather` instructs the event loop to run `step_cell` coroutines concurrently and resume execution of the `simulate` coroutine when all of them have been completed.
* No locks are required for the `Grid` instance since all executions occurs within a single thread. The I/O becomes parallelized as part of the event loop that's provided by `asyncio`. 

* Finally, we can run our code:
```python
grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()

for i in range(5):
    columns.append(str(grid))
    grid = asyncio.run(simulate(grid))

print(columns)
```
    >>>
        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

* the debugging is also possible by simply raising an exception:
```python
async def game_logic(state, neighbors):
    ...
    raise OSError("Problem with I/O")
    ...

asyncio.run(game_logic(ALIVE, 3))
```
    >>>
    Traceback ...
    OSError: Problem with I/O

* it is also easy to add more concurrency. To make `count_neighbors` coroutine, for instance, minimal change to code is needed:
```python
async def count_neighbors(y, x, get):
    ...


async def step_cell(y, x, get, set):
    state = get(y, x)
    neighbors = await count_neighbors(y, x, get)
    next_state = await game_logic(state, neighbors)
    set(y, x, next_state)


grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()

for i in range(5):
    columns.append(str(grid))
    grid = asyncio.run(simulate(grid))

print(columns)
```
    >>>
        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------

The beauty of coroutines is that they decouple your code's instructions for the external environment from the implementation that carries out your wishes. They let you focus on the logic of what you are trying to do instead of wasting your time trying to figure out how to do it concurrently.

## Item 61, Know How to Port Threaded I/O to `asyncio`

Considering advantages of coroutines, how would you port existing codebase to use them? Moving threaded, blocking I/O to coroutines and asynchronous I/O is well supported in Python.

For example. lets take a TCP-based game which guesses a number. Server determines the range of number to consider. Then it returns the guessed number to the client. Finally, server collects report on how good it was on guessing the secret number. 

Here is the example of such server using Threaded blocking I/O.
```python
class EOFError(Exception):
    pass


class ConnectionBase:
    def __init__(self, connection):
        self.connection = connection
        self.file = connection.makefile("rb")
    def send(self, command):
        line = command + "\n"
        data = line.encode()
        self.connection.send(data)
    def receive(self):
        line = self.file.readline()
        if not line:
            raise EOFError("Connection closed")
        return line[:-1].decode()

```
This class is a server, which handles one connection at the a time and maintains client's session state:
```python
import random


WARMER = "Warmer"
COLDER = "Colder"
UNSURE = "Unsure"
CORRECT = "Correct"


class UnknownCommandError(Exception):
    pass


class Session(ConnectionBase):
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state(None, None)
    def _clear_state(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.secret = None
        self.guesses = []
    def loop(self):
        while command := self.receive():
            parts = command.split(" ")
            if parts[0] == "PARAMS":
                self.set_params(parts)
            if parts[0] == "NUMBER":
                self.send_number()
            if parts[0] == "REPORT":
                self.receive_report(parts)
            else:
                raise UnknownCommandError(command)
    def set_params(self, parts):
        assert len(parts) == 3
        lower = int(parts[1])
        upper = int(parts[2])
        self._clear_state(lower, upper)
    def next_guess(self):
        if self.secret is not None:
            return self.secret
        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess
    def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        self.send(format(guess))
    def receive_report(self, parts):
        assert len(parts) == 2
        decision = parts[1] 
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last
        print(f"Server: {last} is {decision}")
```
* The client is implimented using a statful class:
```python
import contextlib
import math


class Client(ConnectionBase):
    def __init__(self, *args):
        super().__init__(*args)
        self._clear_state()
    def _clear_state(self):
        self.secret = None
        self.last_distance = None
    @contextlib.contextmanager
    def session(self, lower, upper, secret):
        print(f"Guess an number between {lower} and {upper}!"
              f"Shhhhh, it\'s a {secret}.")
        self.secret = secret
        self.send(f"PARAMS {lower} {upper}")
        try:
            yield
        finally:
            self._clear_state()
            self.send("PARAMS 0 -1")
    def request_number(self, count):
        for _ in range(count):
            self.send("NUMBER")
            data = self.receive()
            yield int(date)
            if self.last_distance == 0:
                return
    def report_outcome(self, number):
        new_distance = math.fabs(number - self.secret)
        decision = UNSURE
        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            pass
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER
        self.last_distance = new_distance
        self.send(f"REPORT {decision}")
        return decision
```
* We can run the server by having one thread listen on a socket and swamp additional threads ti handle the new connections.
```python
import socket
from threading import Thread


def handle_connection(connection):
    with connection:
        session = Session(connection)
        try:
            session.loop()
        except EOFError:
            pass

def run_server(address):
    with socket.socket() as listener:
        listener.bind(address)
        listener.listen()
        while True:
            connection, _ = listener.accept()
            thread = Thread(target=handle_connection,
                            args=(connection,),
                            daemon=True)
            thread.start()
```
* The Client runs on the main thread and return the results of the guessing game to the caller. This code explicitly exercises a variety of Python language features, so that below it can be shown what it takes to port these over to using coroutines:
```python
def run_client(address):
    with socket.create_connection(address) as connection:
        client = Client(connection)
        with client.session(1, 5, 3):
            results = [(x, client.report_outcome(x)) 
                        for x in client.request_number(5)]
        with client.session(10, 15, 12):
            for number in client.request_number(5):
                outcome = client.report_outcome(number)
                results.append((number, outcome))
    return results
```
* Finally, we can glue it together and confirm that it works:
```python
def main():
    address = ("127.0.0.1", 1234)
    server_thread = Thread(
        target=run_server, args=(address,), daemon=True)
    server_thread.start()
    results = run_client(address)
    for number, outcome in results:
        print(f"Client: {number} is {outcome}")


main()
```


# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)