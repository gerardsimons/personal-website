import os
import time
import datetime
import csv

import queue

from threading import Thread
from multiprocessing import Process, Queue, Lock


fp = open(f"results.csv", 'w')
file_lock = Lock()

csv_writer = csv.writer(fp, delimiter='\t', quoting=csv.QUOTE_NONE)
csv_writer.writerow(["tag", "start_time", "end_time", "elapsed"])
result_queue = Queue()

def save_results(size):
    for _ in range(size):
        values = result_queue.get()
        csv_writer.writerow(values)

    # file_lock.acquire()

    # csv_writer.writerow([tag, start_t, end_t])

    # file_lock.release()

def fibonacci(n): 
    if n<0: 
        raise ValueError("Incorrect input") 
    # First Fibonacci number is 0 
    elif n==1: 
        return 0
    # Second Fibonacci number is 1 
    elif n==2: 
        return 1
    else: 
        return fibonacci(n-1)+fibonacci(n-2) 

def save_fibonacci(tag, n):
    t = time.time()
    result = fibonacci(n)
    # print(f"Fibonacci {n} = {result}")
    result_queue.put((tag, t, time.time()))
    # print("Done.")

def process_print(*args, **kwargs):
    print(os.getpid(), "-", *args, **kwargs)

def produce(q, num, delay, n_consumers):
    for i in range(1, num):
        process_print("Produce ", i)
        q.put(i)
        time.sleep(delay)

    # Put a poison pill on the queue for each process
    # Because a process terminates right after receiving one
    # it is guaranteed they all get exactly one
    for _ in range(n_consumers):
        q.put(PoisonPill)


def consume(q, delay):
    process_print("Start")
    while True:
        i = q.get()
        if i is PoisonPill:
            break

        process_print("Got", i)

        print(f"Fibonacci({i}) = {fibonacci(i)}")
        # time.sleep(delay)

    process_print("Stops")


def run_experiment(Runnable, produce_delay, n_tasks, consume_delay, n_consumers):

    print("Run Experiment with Process ... ", end="")
    workers = []

    for i in range(1, n_consumers+1):
        # p = Process(target=consume, args=(queue, consume_delay))
        tag = f"{Runnable.__name__}_{i}"
        p = Runnable(target=save_fibonacci, args=(tag, i+20))
        workers.append(p)
        p.start()

    tic = time.time()

    save_results(len(workers))

    toc = time.time()
    elapsed = datetime.timedelta(seconds=toc - tic)
    print("finished in ", elapsed)
    return elapsed


if __name__ == '__main__':
    N = 10
    process_time = run_experiment(Process, 0.01, 40, 0.1, N)
    threaded_time = run_experiment(Thread, 0.01, 40, 0.1, N)

    speed_up = process_time / threaded_time * 100.0
    # print(f"Speed up = {}"})