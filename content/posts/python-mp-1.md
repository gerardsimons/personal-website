---
title: "Python Multiprocessing I: Concurrency vs Parallelism"
date: 2020-04-15T21:54:27+02:00
draft: true
---

Having recently almost lost my wit doing a project involving the use of Python's multiprocessing library, I thought it would be a good way of well eh processing my near loss of sanity experience by dedicating a few posts on the topic. This will be the first one, where I discuss the difference between concurrency and parallelism, which in Python is implemented as threads vs processes. Making a codebase run truly concurrently is quite tricky, especially where custom communication and synchronization constructs are required. Challenging, but also certainly very rewarding. I can only hope this post will take you from the tricky part to the rewarding part somewhat faster. 

## Python Processes vs Threads
Python is not a very performant language but can be significantly accelerated by utilising more of the hardware available, in particular CPU cores. If you delve into Python even a little bit, you are bound to run into Threads. Threads offer a straightforward way to write simple non-blocking code and is sufficient in many cases, in particular in network-bound ones, like waiting for a HTTP request to return a result. You could use a thread to do some stuff in the background. In certain cases though, this is not enough and you will find yourself in need of more, as you notice the delays between the switch and you notice that it's not doing these things actually at the same time. So why is that?

One reason for this is that although you can do something else while one thread is waiting, you can still not do multiple things at the same time. A more formal distinction can be defined as parallelism vs concurrency. 

## An Important Distinction
Concurrency and parallelism are related terms, often misconceived even as synonyms. The are not the same, and understanding this difference is crucial when you want to build truly performant systems. The important difference between concurrency and parallelism being that the former is more about dealing with a lot of things at same time (giving the illusion of simultaneity) but not actually doing them at the same time. Whereas parallelism does actually execute everything at the same time. The figure below shows the difference. 

![Image](/img/mp-1/concurrency-vs-parallelism.jpg)

Let me given an example to make the distinction clearer: Lets say you go for a run, but just when you leave, you find out your shoelaces are untied. You stop and tie them, but you cannot run and tie your shoe laces at the same time - no, please don't try this and get yourself hurt in a super-awkward manoeuvre. What actually happens in a CPU is that all the information contained in a thread is saved and restored once the thread runs again. This is called **context switching**, and is as might have guessed from the description quite an expensive operation. So how can we actually do things in parallel rather concurrently and avoid the dreadful context switch? Well, your CPU has multiple cores. It might be a good idea to leverage those. Enter the multiprocessing library in Python.

Admittedly the distinction between multiprocessing and multithreading is a bit of an odd one and isn't common to all programming languages. Let's give a little bit of background: when Python was developed it was decided that it should have a **global interpreter lock**, which just means the entire application is wrapped in a huge lock. A lock is a concept from parallel computing that locks a piece of code, in a way reserving it until the locks is released by the specific process. We will talk more about it later, but suffice it to say for now that this decision made it very easy to work with threads safely but does mean that another library was needed to run code truly concurrently.

The way around all the safe but slowish threads is by using processes. The multiprocessing library allows you to execute code truly concurrently. This post will mostly discuss the things I learnt when implementing my own processes including communications. This becomes quite tricky when the lack of the GIL no longer ensure thread safety. 

Independent processes do not require any synchronisation between them and if that's the case for you, then well, lucky you, your life just became a whole lot easier. That's because there are useful things like the `ProcessPoolExecutor` or `MultiProcessingPool` you can use, usually requiring only a couple of lines changes. These are for those kind of tasks that are sometimes called embarassingly parallelizable. In fact many of the higher level libraries often have support for mulitprocessing or there exist parallel versions of them. Are you crunching pandas dataframes, use Dask for example. It's always worth googling your framework of choice and seeing if there are parallelised versions of them. Nevertheless, sometimes you are building something that requires you to create processes yourself. 

Let's first look at the Pools we talked about to further clarify the difference between concurrency and parallelism in terms of actual results. In the code below I run two types of experiments: one involving heavy recursive computation of a fibonacci series, the other just some HTTP get requests that vary in delay. It's crucial for this experiment that one of these actually requires constant computation, whereas the other is just a matter of waiting. You could get the same effect with a long sleep statement or some simple IO work instead of the HTTP get request. Feel free to play around with the experiment parameters to get different results. In fact, results vary per machine, especially the number of workers. There's only so many actual CPU cores a computer has, which has a profound effect on how much your machine can do at one time. Other running processes will also affect it.

Let's look at some experimentation code I wrote that will clarify the differences between concurrency and parallelism, or processes vs threads by using the two types of PoolExcutors. In this sample code I have fibonacci computation code and just HTTP get code. The former being CPU-bound the latter network bound. 

```python
import time
import datetime
import csv
import urllib.request

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def fibonacci(n):
    if n < 0:
        raise ValueError("Incorrect input")
        # First Fibonacci number is 0
    elif n == 1:
        return 0
    # Second Fibonacci number is 1
    elif n == 2:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

# We simulate a HTTP fetch wait request with httpstat
def http_fetch(n): 
    t = time.time()
    response = urllib.request.urlopen(f'https://httpstat.us/200?sleep={n}').read()
    return t, time.time(), response

# Fibonacci wrapped in a cute little timed thingie
def timed_fibonacci(n):
    t = time.time()
    result = fibonacci(n)
    return t, time.time(), result

# Take a PoolExecutor class and run the function fn over all of it's inputs using n_workers workers. Tag is used as the CSV file name
def run_experiment(PoolExecutor, fn, inputs, n_workers, tag):
    print(
        f"Run experiment {PoolExecutor.__name__}:\t running {fn.__name__} over {list(inputs)} among {n_workers} workers ... ",
        end="")
    tic = time.time()
    i = 0

    fp = open(tag + ".csv", 'w')
    csv_writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(["tag", "start_time", "end_time", "elapsed", "result"])

    with PoolExecutor(max_workers=n_workers) as executor:
        for start_t, end_t, result in executor.map(fn, inputs):
            csv_writer.writerow([f"{tag}-{i}", start_t, end_t, end_t - start_t, result])
            i += 1

    toc = time.time()
    elapsed = datetime.timedelta(seconds=toc - tic)
    return elapsed

if __name__ == '__main__':
    fibonacci_inputs = range(34, 42)
    n_workers = len(list(fibonacci_inputs))

    p_time = run_experiment(ProcessPoolExecutor, timed_fibonacci, fibonacci_inputs, n_workers, "process-fibo")
    t_time = run_experiment(ThreadPoolExecutor, timed_fibonacci, fibonacci_inputs, n_workers, "thread-fibo")
    print(f"Process vs Threads Fibonacci tasks speed-up = {(t_time - p_time) / t_time * 100:.2f}%")

    http_get_wait_inputs = range(1000, 1800, 100)
    n_workers = len(list(http_get_wait_inputs))
    p_time = run_experiment(ProcessPoolExecutor, http_fetch, http_get_wait_inputs, n_workers, "process-get")
    t_time = run_experiment(ThreadPoolExecutor, http_fetch, http_get_wait_inputs, n_workers, "thread-get")
    print(f"Process vs Threads HTTP Get tasks speed-up = {(t_time - p_time) / t_time * 100:.2f}%")
```

It should output the total time it took for each, but also write out the results in four separate CSVs. Let's plot the results as a Gantt chart using Plotly. First the Fibonacci results:

{{< figure src="/img/mp-1/process-thread-fibonacci-gantt.png" alt="Hello Friend" position="center" style="border-radius: 8px;" caption="Fibonacci computation times" captionPosition="center" >}}

{{< figure src="/img/mp-1/process-thread-fetch-gantt.png" alt="Hello Friend" position="center" style="border-radius: 8px;" caption="HTTP fetch times" captionPosition="center" >}}

I generated this by running the above code and then loading the results with pandas, subtracting the start-times and plotting them ordered by start time. (LINK TO NOTEBOOK?) It's interesting to see the pattern of process and thread start and end-times. In the case of Fibonacci you can see all threads and processes are said to spawn at the same time, but the actual computation of the processes all happens in parallel, whereas the threads need to be shuffled around and switched so they all get some piece of the computation which causes longer run-times overall. However, the story is very different for the HTTP get stuff, where the overhead of the processes is detrimental for performance since we are basically just waiting for something to happen outside of our control (a HTTP fetch response in this case)

From these results we can really back up the notion that processes should be used when your task is CPU bound, whereas threads are just as good or often better at doing at doing things that involve just waiting around for something outside of the CPU's control (the CPU is not the bottleneck)

However, as mentioned before, what if you do need some kind of communication between your processes, for example because the result of one routine is dependent on the result of another, this becomes challenging to do with PoolExecutors. Implementing your own processes from scratch will then become necessary. And it is this subject, which although fun and eventually very rewarding can also be an excruciatingly tricky beast to handle, that is the main driver behind these posts. It's a good way for me to digest my own learnings and hopefully provide some solace to you as well, my concurrent comrade. So let's get down to it.

## Variable Space Isolation
Another major down-side of running processes is that we can no longer access all the variables everywhere. Or rather we can, but we are not actually accessing what we think we are. This is at the very root of the challenge in parallelisation. Each process is on its own and only those bits of data that you decide to pass between them is shared. The method of sharing is also important as each bit of communication incurs a certain penalty as one process is basically holding up another process.

Let's look at this challenge in the most simple context. Accessing variables in such a manner doesn't raise an error but it's just set to a different value, each process is accessing its own version of that variable, it has its own scope. 

```python
import os
import time
from multiprocessing import Process
from threading import Thread

# Global declaration of x
x = 0

def access_x(tag):
    pid = os.getpid()
    for _ in range(3):
        time.sleep(1)
        print(f"{tag}-{pid} thinks X is {x}")

t = Thread(target=access_x, args=('Thread',))
p = Process(target=access_x, args=('Process',))
t.start()
p.start()

main_pid = os.getpid()
for _ in range(3):
    x += 1
    print(f"Main-{main_pid} sets X to {x}")
    time.sleep(1)
```

Which will output something like this, though obviously your process ids may differ as these are allocated by your operating system at random.

```
Thread-70572 thinks X is 0
Main-70572 sets X to 1
Process-70575 thinks X is 0
Thread-70572 thinks X is 1
Process-70575 thinks X is 0
Main-70572 sets X to 2
Thread-70572 thinks X is 2
Process-70575 thinks X is 0
Main-70572 sets X to 3
```

A few things stand out in this simple demonstration. One is that the thread and the main thread share the same process ID (PID), a clear indicator that it's just the same process after all. Second, and very much related to the first is that the Process that does have a different PID code doesn't get the updates on variable X, whereas the Thread does. Processes have their own variable space and are not hindered (or helped) by the global interpreter lock.

This really exemplifies what multiprocessing is all about. How do we effectively communicate states between processes so that we can still leverage as much as possible the parallelism or independence between them. We will need to be clever about this. Fortunately the Python standard library is chock full of useful constructs to help us out. Cool sounding things like `Locks`, `Barriers`, `Values`, `Queues` and `Pipes` to name just a few. I will be discussing more detailed stuff in upcoming posts. 

 I do hope this post was already useful in understanding the subtle but important difference between parallelism and concurrency and how that difference translates to threads and processes in Python. Stay tuned for more.