import os
import time
import datetime
import csv
import urllib.request

import queue

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Thread
from multiprocessing import Process, Queue, Lock, cpu_count


file_lock = Lock()

result_queue = Queue()

def save_results(size):
    for _ in range(size):
        values = result_queue.get()
        csv_writer.writerow(values)

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

def http_fetch(n):
    t = time.time()
    # print("Fetching ", f'https://httpstat.us/200?sleep={n}')
    response = urllib.request.urlopen(f'https://httpstat.us/200?sleep={n}').read()
    return t, time.time(), response

def save_fibonacci(tag, n):
    t = time.time()
    result = fibonacci(n)
    # print(f"Fibonacci {n} = {result}")
    result_queue.put((tag, t, time.time()))
    # print("Done.")

def timed_fibonacci(n):
    t = time.time()
    result = fibonacci(n)
    return t, time.time(), result

def run_experiment(PoolExecutor, fn, inputs, n_workers, tag):

    print(f"Run experiment {PoolExecutor.__name__}:\t running {fn.__name__} over {list(inputs)} among {n_workers} workers ... ", end="")
    tic = time.time()
    i = 0

    fp = open(tag + ".csv", 'w')
    csv_writer = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(["tag", "start_time", "end_time", "elapsed", "result"])

    with PoolExecutor(max_workers=n_workers) as executor:
        for start_t, end_t, result in executor.map(fn, inputs):
            # print(f"Result #{i}", result)
            csv_writer.writerow([f"{tag}-{i}", start_t, end_t, end_t - start_t, result])
            i+=1

    toc = time.time()
    elapsed = datetime.timedelta(seconds=toc - tic)
    print("Total elapsed = ", elapsed)
    return elapsed


cpu_usage_history = []
active = False
def check_cpu_usage():
    import psutil
    global active
    active = True

    def __check():
        while active:
            cpu_usage = psutil.cpu_percent()
            # print("CPU%", cpu_usage)
            cpu_usage_history.append(cpu_usage)
            time.sleep(0.5)

    t = Thread(target=__check)
    t.start()
    return t

if __name__ == '__main__':
    check_thread = check_cpu_usage() 
    
    
    inputs = range(30, 42)
    print("Fibonacci")    
    n_workers = len(list(inputs))

    
    # print("CPU usage = ", cpu_usage_history)
    # print("CPU Usage mean = ", sum(cpu_usage_history) / len(cpu_usage_history), )
    # cpu_usage_history.clear()
    # p_time = run_experiment(ProcessPoolExecutor, timed_fibonacci, inputs, n_workers, "process")
    # t_time = run_experiment(ThreadPoolExecutor, timed_fibonacci, inputs, n_workers, "thread")
    # print(f"Process vs Threads speed-up = {(t_time-p_time)/t_time*100:.2f}%", )

    p_time = run_experiment(ProcessPoolExecutor, http_fetch, inputs, n_workers, "process-get")
    t_time = run_experiment(ThreadPoolExecutor, http_fetch, inputs, n_workers, "thread-get")
    print(f"Process vs Threads speed-up = {(t_time-p_time)/t_time*100:.2f}%", )

    # print("HTTP Get")
    # inputs = range(1000, 2000, 100)
    # t_time = run_experiment(ThreadPoolExecutor, http_fetch, inputs, n_workers)
    # p_time = run_experiment(ProcessPoolExecutor, http_fetch, inputs, n_workers)
    # # print("CPU Usage mean = ", sum(cpu_usage_history) / len(cpu_usage_history))
    # print("CPU usage = ", cpu_usage_history)
    # print(f"Process vs Threads speed-up = {(t_time-p_time)/t_time*100:.2f}%")

    active = False

    # speed_up = process_time / threaded_time * 100.0
    # print(f"Speed up = {}"})