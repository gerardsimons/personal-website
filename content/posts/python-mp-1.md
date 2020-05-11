---
title: "Python Multiprocessing I: Concurrency vs Parallelism"
date: 2020-04-15T21:54:27+02:00
cover: "/img/mp-1/concurrency-vs-parallelism.jpg" 
---

Having recently almost lost my wit doing a project involving Python's multiprocessing library for [Captain AI](https://www.captainai.com/), I thought it would be a good way of well eh processing my experience of almost going insane by dedicating some words on it. This will be the first part, where I discuss the difference between concurrency and parallelism, which in Python is implemented as threads vs processes. Making a codebase run truly concurrently is quite challenging, especially where custom communication and synchronisation constructs are required. Challenging, but also very rewarding in the end, if you haven't lost your mind yet by that time. I can only hope this post will take you from the challenging part to the rewarding part somewhat faster. 

## Python Processes vs Threads
Python is not a very performant language but can be significantly accelerated by utilising more of the available hardware, in particular CPU cores. If you delve into Python even a little bit, you are bound to run into Threads. Threads offer a straightforward way to write simple non-blocking code and is sufficient in many cases, in particular in network-bound ones, like waiting for a HTTP request to complete. In certain cases though, this is not enough and you will find yourself in need of even more performance in particular in those where you are really pushing the limits of your CPU power. It seems the threads can only use so much of it. So why is that?

One reason for this is that even though your machine can do something else while one thread is waiting, it still can not do multiple things at the same time. This is what we mean when we talk about parallelism vs concurrency. 

## An Important Distinction
Concurrency and parallelism are related terms, often misconceived even as synonyms, but they are not the same! Understanding this distinction is crucial when you want to build truly performant systems. The important difference between concurrency and parallelism being that the former is more about dealing with a lot of things at same time (giving the illusion of simultaneity) but not actually doing them at the same time. Whereas parallelism does actually execute everything at the same time. 

Let me give a real life analogy to make this distinction clear. Let's say you are making breakfast. You want to make toast, boil an egg and brew some coffee. If you're like me you try to do these things at the same time, but it's not easy. Once the coffee is brewing you can do other things while you wait for it to finish but it might be more difficult to spread jam over your toast while also peeling an egg. You would constantly have to switch tasks to get any kind of speed-up.

This problem is called **context switching**, and it's what happens when you run multiple threads as well, the single CPU core switches tasks which is good for waiting around tasks but not so much for computationally intensive tasks. So how can we actually do things in parallel and avoid the dreadful context switch? Well, your CPU has multiple cores. It might be a good idea to leverage those. Enter the multiprocessing library in Python.

## The Dreaded GIL
Let's give a little bit of background: when Python was developed it was decided that it should have a **global interpreter lock**, which just means the entire application is wrapped in a huge lock. A lock is a concept from parallel computing that locks a piece of code, in a way reserving it until the locks is released by the specific process. We will talk more about those later, but suffice it to say for now that this decision made it very easy to work with threads safely and avoid strange errors but it does mean another library was needed for true parallelisation. This can be accomplished by using processes. This becomes quite tricky when the lack of the GIL no longer ensure thread safety. 

## Pools for Easy Parallelisation
Independent processes do not require any synchronisation between them and if that's the case for you, then well, lucky you, your life just became a whole lot easier. That's because there are useful things like the `ProcessPoolExecutor` or `MultiProcessingPool` you can use, usually requiring only a couple of lines changes. These are for those kind of tasks that are sometimes called embarrassingly parallelisable. I often use this if I am doing something with multiple files. It is usually just two lines of code changes. Going from

```python 
for f in files:
    ret = some_function(f)
    print(ret)
```

To this

```python
with ProcessPoolExecutor() as executor:
    for ret in executor.map(some_function, files):
        print(ret)
```
You can already expect a major speed-up. In fact many of the higher level libraries often have support for multiprocessing or have parallel versions of them. Are you crunching pandas dataframes? Use [Dask](https://dask.org/). [Ray](https://github.com/ray-project/ray) has some nice methods of parallelising your processes across machines even. It's always worth googling your framework of choice and seeing if there are parallelised versions of them. Nevertheless, sometimes you are building something that requires you to create processes yourself. 

## Performance Differences
Let us get back to the concurrency vs parallelism thing by looking at the pools we talked about in terms of actual performance. In the code below there are two types of experiments: one involving heavy recursive computation of a Fibonacci series, the other just some HTTP get requests that vary in delay. It's crucial for this experiment that one of these actually requires constant computation, whereas the other is just a matter of waiting. You could get the same effect with a long sleep statement or some simple IO work instead of the HTTP get request. Feel free to play around with the experiment parameters to get different results. In fact, results vary per machine, especially the number of workers. There's only so many actual CPU cores a computer has, which has a profound effect on how much your machine can do at one time. Other running processes will also affect it.


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

These figures were generated running the above code and loading the results with pandas, subtracting the start-times and plotting them ordered by start time. Find the notebook code for it [here](https://github.com/gerardsimons/personal-website/blob/master/notebooks/plot_gantt_results.ipynb). It's interesting to see the pattern of process and thread start and end-times. In the case of Fibonacci you can see all threads and processes spawn at the same time, but the actual computation of the processes all happens in parallel, whereas the threads need to be shuffled around and switched so they all get some piece of the computation which causes longer run-times overall. The story is very different however for the HTTP get routines, where the overhead of the processes is detrimental for performance since we are basically just waiting for something to happen outside of our control (a HTTP fetch response in this case) and the additional setup of processes just makes things slower.

From these results we can really back up the notion that processes should be used when your task is CPU bound, whereas threads are just as good or often better at doing at doing things that involve just waiting around for something outside of the CPU's control (the CPU is not the bottleneck)

However, as mentioned before, what if you do need some kind of communication between your processes, for example because the result of one routine is dependent on the result of another, this becomes challenging to do with `PoolExecutors`. Implementing your own processes from scratch will then become more interesting. And it is this subject, which although fun and eventually very rewarding can also be an excruciatingly tricky beast to handle, that is the main driver behind these posts. It's a good way for me to digest my own learnings and hopefully provide some solace to you as well, my concurrent comrade. So let's get down to it.

## Variable Space Isolation
Before I finish this post, let's take a look at the challenge in its smallest form. The challenge being that we can not access variables from other processes like we are used to with threads. Or rather we can, but we are not actually accessing what we think we are. This is at the very root of the challenge in parallelisation. Each process is on its own and only those bits of data that you decide to pass between them is shared (and those bits need to be pickle-able!). How and when you share also becomes important as each bit of communication will create overhead and in the worst case cause complete deadlock of your system where each process is politely waiting for the other, forever!


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

A few things stand out in this simple demonstration. One is that the thread and the main thread share the same process ID (PID), a clear indicator that it's just the same process after all. On the contrary, the process does get a different PID. The process doesn't get the updates on variable X, whereas the thread does. Processes have their own variable space and are not hindered (or helped!) by the global interpreter lock.

This really exemplifies what multiprocessing is all about. How do we effectively communicate states between processes so that we can still parallelise things as much as possible. We will need to be clever about this. Fortunately the Python standard library is chock full of useful constructs to help us out. Cool sounding things like `Locks`, `Barriers`, `Values`, `Queues` and `Pipes` to name just a few. I will be discussing more detailed stuff like this in upcoming posts. 

 I hope this post was already useful in understanding the subtle but important difference between parallelism and concurrency and how that difference translates to threads and processes in Python. I am still very much a rookie in this topic, so if you see anything that's wrong, or if you just have something interesting to share let me know in the comments! Stay tuned for more. 