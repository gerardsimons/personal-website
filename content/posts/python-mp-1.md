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

Admittedly the distinction between multiprocessing and multithreading is a bit of an odd one and not one I have seen in other programming languages. A little bit of background: when Python was developed it was decided that it should have a **global interpreter lock**, which just means the entire application is wrapped in a huge lock. A lock is a concept from parallel computing that locks a piece of code, in a way reserving it until the locks is released by the specific process. We will talk more about it later, but suffice it to say for now that this decision made it very easy to work with threads safely but does mean that another library was needed to run code truly concurrently.

The way around all the safe but slowish threads is by using processes. The multiprocessing library allows you to execute code truly concurrently. This post will mostly discuss the things I learnt when implementing my own processes including communications. This becomes quite tricky when the lack of the GIL no longer ensure thread safety. 

Independent processes do not require any synchronisation between them and if that's the case for you, then well, lucky you, your life just became a whole lot easier. That's because there are useful things like the `ProcessPoolExecutor` or `MultiProcessingPool` you can use, usually requiring only a couple of lines changes. These are for those kind of tasks that are sometimes called embarassingly parallelizable. In fact many of the higher level libraries often have support for mulitprocessing or there exist parallel versions of them. Are you crunching pandas dataframes, use Dask for example. It's always worth googling your framework of choice and seeing if there are parallelised versions of them. Nevertheless, sometimes you are building something that requires you to create processes yourself. 

Let's first look at the Pools we talked about to further clarify the difference between concurrency and parallelism in terms of actual results. In the code below I run two types of experiments: one involving heavy recursive computation of a fibonacci series, the other just some HTTP get requests that vary in delay. It's crucial for this experiment that one of these actually requires constant computation, whereas the other is just a matter of waiting. You could get the same effect with a long sleep statement or some simple IO work instead of the HTTP get request. Feel free to play around with the experiment parameters to get different results. In fact, results vary per machine, especially the number of workers. There's only so many actual CPU cores a computer has, which has a profound effect on how much your machine can do at one time. Other running processes will also affect it.

<EXAMPLE OF POOL EXECUTOR ------- PLUS RESULTS>

However, as mentioned before, what if you do need some kind of communication between your processes, for example because the result of one routine is dependent on the result of another, this becomes challenging to do with PoolExecutors. Implementing your own processes from scratch will then become necessary. And it is this subject, which although fun and eventually very rewarding can also be an excruciatingly tricky beast to handle, that is the main driver behind these posts. It's a good way for me to digest my own learnings and hopefully provide some solace to you as well, my concurrent comrade. So let's get down to it.

<MAYBE A PLOT OF THREAD START AND END TIMES?>

## Basic Communication
The major down-side of running multiple processes is that we can no longer access all the variables everywhere. Or well we can, but we are not actually accessing what we think we are. This is really at the very root of the challenge in parallelisation. Each process is on its own and only those bits of data that you decide to pass between them is shared. The method of sharing is also important as each bit of communication incurs a certain penalty as one process is basically holding up another process.

One of the issues with multiprocessig is that it can be a silent killer. It doesn't necessarily throw an error but it's just set to a different value, each process is basically accessing it's own version of that variable, it has its own scope. The example below will show this more clearly

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

A few things stand out in this simple demonstration. One is that the thread and the main thread share the same process ID (PID), a clear indicator that it's just the same process after all. Second, and very much related to the first is that the Process that does have a different PID code doesn't get the updates on variable X, whereas the Thread does. Processes have their own variable space.

This really exemplifies what multiprocessing is all about. How do we effectively communicate states between processes so that we can still leverage as much as possible the parallelism or independence between them. We will need to be clever about this. Fortunately the Python standard library is chock full of useful constructs to help us out. Cool sounding things like `Locks`, `Barriers`, `Values`, `Queues` and `Pipes` to name just a few. I will be discussing these in upcoming posts. Stay tuned!