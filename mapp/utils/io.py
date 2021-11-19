import json
import os
import ijson.backends.yajl2 as ijson
from collections import OrderedDict
from timeit import default_timer as timer
import formatting as fmt
import profiler
from numpy import random
from itertools import islice

from .utils import get_elapsed_seconds, get_key


def __save_to_json__(filename, obj, indent_num=2):
    with open(filename, "w") as f:
        print(fmt.WAIT_SYMBOL, "Saving:", filename)
        start = timer()
        json.dump(obj, f, indent=indent_num)
        end = timer()
    print(fmt.OK_SYMBOL, "Saved. Took:", get_elapsed_seconds(start, end), "seconds\n")


def save_list_to_json(filename, data, indent_num=2):
    input_list = [x for x in data]

    __save_to_json__(filename, input_list, indent_num=2)


def save_dict_to_json(filename, data, ordered=True, indent_num=2):
    data = data.copy()

    if ordered:
        data = OrderedDict(sorted(data.items(), key=lambda d: get_key(d[0])))

    __save_to_json__(filename, data, indent_num=2)


def split_dataset(path, output_dir):
    print(fmt.WAIT_SYMBOL, "Splitting dataset ", path, "to", output_dir)
    start = timer()
    f = open(path, "rb")

    objects = ijson.items(f, "item")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, obj in enumerate(objects):
        path = os.path.join(output_dir, str(i) + ".json")

        with open(path, "w") as out:
            json.dump(obj, out, indent=2)
        out.close()

    end = timer()
    print(
        fmt.OK_SYMBOL,
        "Finished splitting. Took",
        get_elapsed_seconds(start, end),
        "seconds",
    )


def save_dataset(filename, dataset, format_type="turtle"):
    with open(filename, "wb") as f:
        print(fmt.WAIT_SYMBOL, "Saving:", filename)
        start = timer()
        dataset.serialize(f, format=format_type)
        end = timer()
    print(fmt.OK_SYMBOL, "Saved. Took:", get_elapsed_seconds(start, end), "seconds\n")


def save_graph(filename, graph, format_type="nt"):
    with open(filename, "wb") as f:
        print(fmt.WAIT_SYMBOL, "Saving:", filename)
        start = timer()
        graph.serialize(f, format=format_type)
        end = timer()
    print(fmt.OK_SYMBOL, "Saved. Took:", get_elapsed_seconds(start, end), "seconds\n")


@profiler.do_profile()
# TODO: Change to new file structure
def get_dataset_indexes(path, count=None):
    datasets = []
    print(fmt.WAIT_SYMBOL, "Gathering information on the dataset...")

    for f in os.listdir(path):
        if f.endswith(".json"):
            datasets.append(int(f.split(".")[0]))

    if count:
        return random.sample(datasets, count)
    else:
        return datasets


@profiler.do_profile()
def load_json(path, index=None, verbose=True):
    try:
        f = open(path, "r")

        if verbose:
            print(fmt.WAIT_SYMBOL, "Loading file:", path)
        try:
            start = timer()

            if index:
                objects = ijson.items(f, "item")

                for obj in islice(objects, index, index + 1):
                    # Only loads one object always, so this is messy but works
                    json_data = obj

            else:
                json_data = json.load(f)
            end = timer()

            if verbose:
                print(
                    fmt.OK_SYMBOL,
                    "Loaded. Took:",
                    get_elapsed_seconds(start, end),
                    "seconds",
                )
        except (ValueError) as error:
            print(error)
            return None
        f.close()
        return json_data
    except (IOError) as error:
        print(error)
        return None
