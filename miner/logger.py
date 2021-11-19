from collections import defaultdict
import io_handler as io
import time
import constants as c


class Logger(object):
    def __init__(self, log_name):
        self.log = defaultdict()
        self.path = c.LOG_DIR + log_name

    def log_run(self, num_threads, num_triples, exec_time, mem_usage):
        timestr = time.strftime("%Y_%m_%d-%H:%M:%S")
        self.log[timestr] = {
            "threads": num_threads,
            "total_triples": num_triples,
            "triples_per_s": round((float(num_triples) / exec_time), 2),
            "run_time": exec_time,
            "maximum_memory_usage": mem_usage,
        }

    def save(self):
        old_log = io.load_json(self.path)

        if old_log is not None:
            self.log.update(old_log)

        io.save_dict_to_json(self.path, self.log)
