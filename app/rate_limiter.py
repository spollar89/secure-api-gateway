import threading
import time

rate = 0
lock = threading.Lock()

def rate_increase():
    global rate
    if rate >= 100:
        raise Exception("Rate limit exceeded")
    with lock:
        rate += 1

def rate_decrease():
    global rate
    if rate <= 0:
        raise Exception("Rate cannot be negative")
    with lock:
        rate -= 1
        