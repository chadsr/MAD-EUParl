import argparse
from timeit import default_timer as timer
from timing import get_elapsed_seconds
import os
from miner import Miner

import constants as c, io_handler as io, downloader as dl, formatting as fmt

import logging

start = timer()

logging.basicConfig(filename='execution_time.log', format='%(asctime)s %(message)s', filemode='w', level=logging.INFO)

print (fmt.INFO_SYMBOL, "Data directory:", c.DATA_DIR, "\n")

parser = argparse.ArgumentParser()
parser.add_argument("--update", help="Will fetch the latest dataset and then run", action="store_true")
parser.add_argument("--threads", help="Used to specify the number of threads the miner should utilise. Takes an integer, or if left out, uses cpu thread count as default.", type=int)

args = parser.parse_args()

if args.threads:
    num_threads = args.threads
else:
    num_threads = os.cpu_count()

print (fmt.INFO_SYMBOL, "Using", num_threads, "thread(s).\n")

updated = False
if args.update:
    print (fmt.WAIT_SYMBOL, "Downloading latest datasets...")
    updated = dl.download_datasets()
else:
    print (fmt. WARNING_SYMBOL, "Using existing datasets")

miner = Miner()
miner.start(num_threads)

end = timer()

total_time = get_elapsed_seconds(start, end)
print (fmt.INFO_SYMBOL ,"Total execution time:", total_time, "seconds")
logging.info("Datasets updated: "+str(updated)+" Number of threads: "+str(num_threads)+" Execution time: "+str(total_time))
