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
    env = env.environ.copy()
    env["password"] = "4(;QlJ?mVXv?^|+q@UmR%eQaq|Aqh):?"
    proc = subprocess.Popen(
        ["openssl", "enc", "-des3", "-pass", "env:password"],
        env=env
        stdin=subprocess.PIPE
        stdout=subprocess.PIPE)
        






# 
* [Back to repo](https://github.com/almazkun/effective_python#effective_python)