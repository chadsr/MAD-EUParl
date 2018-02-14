"""The initiation of the miner."""

import memory_profiler
import argparse
from timeit import default_timer as timer
from timing_handler import get_elapsed_seconds
import os
from collections import defaultdict
from multiprocessing.managers import BaseManager, DictProxy
from miner import Miner
from logger import Logger

import constants as c
import downloader as dl
import formatting as fmt


class DictManager(BaseManager):
    pass


DictManager.register('defaultdict', defaultdict, DictProxy)

logger = Logger("runtime.json")

print(fmt.INFO_SYMBOL, "Data directory:", c.DATA_DIR, "\n")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--update", help="Will fetch the latest dataset and then run", action="store_true")
parser.add_argument(
    "--threads", help="Used to specify the number of threads the miner should utilise. Takes an integer, or if left out, uses cpu thread count as default.", type=int)
parser.add_argument(
    "--mep-limit", help="Used to specify the number of MEPs to process from the dataset.", type=int)
parser.add_argument(
    "--dossier-limit", help="Used to specify the number of dossiers to process from the dataset.", type=int)
parser.add_argument(
    "--vote-limit", help="Used to specify the number of votes to process from the dataset.", type=int)

args = parser.parse_args()

if args.threads:
    num_threads = args.threads
else:
    num_threads = os.cpu_count()

print(fmt.INFO_SYMBOL, "Using", num_threads, "thread(s).\n")

if args.update:
    print(fmt.WAIT_SYMBOL, "Downloading latest datasets...")
    dl.download_datasets()
else:
    print(fmt. WARNING_SYMBOL, "Using existing datasets")

start = timer()

manager = DictManager()
manager.start()
miner = Miner(manager)

mem_usage = memory_profiler.memory_usage((miner.start, (num_threads, args.mep_limit, args.dossier_limit, args.vote_limit)))
max_mem_usage = max(mem_usage)

end = timer()

total_time = get_elapsed_seconds(start, end)
print(fmt.INFO_SYMBOL, "Total execution time:", total_time, "seconds")

logger.log_run(num_threads, miner.total_triples, total_time, int(round(max_mem_usage)))
logger.save()
