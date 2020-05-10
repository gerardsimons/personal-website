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

def http_fetch(n):
    t = time.time()
    response = urllib.request.urlopen(f'https://httpstat.us/200?sleep={n}').read()
    return t, time.time(), response


def timed_fibonacci(n):
    t = time.time()
    result = fibonacci(n)
    return t, time.time(), result


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
            # print(f"Result #{i}", result)
            csv_writer.writerow([f"{tag}-{i}", start_t, end_t, end_t - start_t, result])
            i += 1

    toc = time.time()
    elapsed = datetime.timedelta(seconds=toc - tic)
    print("Total elapsed = ", elapsed)
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
