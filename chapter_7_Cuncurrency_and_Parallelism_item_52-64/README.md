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
    for _ in range(how_many)
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
```


# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)