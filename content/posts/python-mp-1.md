---
title: "Python Multiprocessing"
date: 2020-04-15T21:54:27+02:00
draft: true
---

Having recently almost lost my wit doing a project involving heavy use of Python's multiprocessing library, I thought it would be a good way of well eh processing my near loss of sanity experience by dedicating a few posts on it. This will be the first one, where I discuss the difference between concurrency and parallelism, which in Python is implemented as threads vs processes. Making a codebase run truly concurrently is quite tricky, especially where custom communication and synchronization constructs are required. Challenging, but also certainly very rewarding. I can only hope this post will take you from the tricky part to the rewarding part somewhat faster. 

Python is not a very performant language but can be significantly accelerated by utilising more of the hardware available, in particular CPU cores. If you delve into Python even a little bit, you are bound to run into Threads. Threads offer a straightforward way to write simple non-blocking code and is sufficient in many cases, in particular cases where you are network bound, like waiting for a HTTP request to return a result. You could use a thread to do some stuff in the background. In certain cases though, this is not enough and you will find yourself in need of more, as you notice the delays between the switch and you notice that it's not doing these things actually at the same time. So why is that?

One reason for this is that although you can do something else while one thread is waiting, you can still not do multiple things at the same time. A more formal distinction can be defined as parallelism vs concurrency. 

Concurrency and parallelism are related terms but not the same, and often misconceived as the similar terms. The crucial difference between concurrency and parallelism is that concurrency is about dealing with a lot of things at same time (gives the illusion of simultaneity) or handling concurrent events essentially hiding latency. On the contrary, parallelism is about doing a lot of things at the same time for increasing the speed. (Totally not clear)

As an example imagine going for a run, finding out your shoelaces are untied. You stop and tie them, but you cannot run and tie your shoe laces at the same time - or can you?! No, please don't get yourself hurt in a super-awkward manoeuvre. What actually happens in a CPU is that all the information contained in a thread is saved and restored once the thread runs again. This is called context switching, and is, as it sounds, quite a costly operation. So how can we actually do things in parallel rather concurrently and avoid the context switch? Enter the multiprocessing library.

Admittedly the distinction between multiprocessing and multithreading is a bit of an odd one and not one I have seen in other programming languages. When Python was developed it was decided that it should have a **global interpreter lock**, which just means the entire application is wrapped in a huge lock. A lock is a concept from parallel computing that locks a piece of code, in a way reserving it until the locks is released by the specific process. We will talk more about it later, but suffice it to say for now that this decision made it very easy to work with threads safely but does mean that another library was needed to run code truly concurrently.

But there is a way around all the safe fluffy threads; by using multiprocessing. Multiprocessing allows you to truly execute code concurrently. This post will mostly discuss the things I learnt when implementing my own processes including communications. This becomes quite tricky when the lack of the GIL no longer ensure thread safety. 

Independent processes do not require any synchronisation between them. If that's the case for you, then well, lucky you, your life just became a whole lot easier. That's because there are objects like the `ProcessPoolExecutor` or `MultiProcessingPool` you can use, usually requiring only a couple of lines changes. 

However, if you do need some kind of communication between your processes, for example because one's result is dependent on the result of another, implementing your own processes from scratch becomes interesting. This matter, which although fun and eventually very rewarding can also be an excruciatingly tricksy beast to handle, and is this the reason for me writing these posts. Good for me to digest my own learnings and hopefully provide some solace to you, my concurrent brother in arms.

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

Which will output something like this, though obviously your process ids may differ as these are allocated by your operating system.

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

A few things stand out in this simple demonstration. One is that the thread and the main thread share the same PID, another clear indicator that it's just the same process after all. Second, and very much related to the first is that the Process that does have a different PID code doesn't get the updates on variable X, whereas the Thread does.

Annoying isn't it? Well yes, but let's also see the advantages. We talked about concurrency vs parallelism before. Now let's see the difference in action. 


Now to come back to the concurrency vs parallelisation question let's do some benchmarks. 

This really exemplifies what multiprocessing is all about. How do we effectively communicate states between processes so that we can still leverage parallelim, not concurrency, as much as possible. In the next post I will talk about some of these communication constructs, their uses and potential pitfalls. Stay tuned.