import datetime
from timeit import default_timer as timer

def get_elapsed_seconds(start, end):
    elapsed = round(end - start, 2)
    return elapsed
