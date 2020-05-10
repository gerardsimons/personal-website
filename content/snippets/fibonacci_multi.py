# F(n + k) = F(n + 1) * F(K) + F(n) * F(k - 1)
# https://stackoverflow.com/questions/16464498/parallelize-fibonacci-sequence-generator

def fibonacci_single(n): 
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

def fibonacci_multi():
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

