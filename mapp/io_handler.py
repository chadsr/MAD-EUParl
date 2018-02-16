import json as json
import ijson.backends.yajl2 as ijson
from collections import defaultdict, OrderedDict
from timeit import default_timer as timer
from timing_handler import get_elapsed_seconds
import formatting as fmt
import random
from itertools import islice
import os

import profiler


def save_dataset(filename, dataset, format_type='turtle'):
    with open(filename, 'wb') as f:
        print(fmt.WAIT_SYMBOL, 'Saving:', filename)
        start = timer()
        dataset.serialize(f, format=format_type)
        end = timer()
    print(fmt.OK_SYMBOL, 'Saved. Took:',
          get_elapsed_seconds(start, end), "seconds\n")


def save_graph(filename, graph, format_type='nt'):
    with open(filename, 'wb') as f:
        print(fmt.WAIT_SYMBOL, 'Saving:', filename)
        start = timer()
        graph.serialize(f, format=format_type)
        end = timer()
    print(fmt.OK_SYMBOL, 'Saved. Took:',
          get_elapsed_seconds(start, end), "seconds\n")


def get_key(key):
    try:
        return int(key)
    except ValueError:
        return key


def save_dict_to_json(filename, data, ordered=True, indent_num=2):
    if ordered:
        data = OrderedDict(sorted(data.items(), key=lambda d: get_key(d[0])))

    with open(filename, 'w') as f:
        print(fmt.WAIT_SYMBOL, 'Saving:', filename)
        start = timer()
        json.dump(data, f, indent=indent_num)
        end = timer()
    print(fmt.OK_SYMBOL, 'Saved. Took:', get_elapsed_seconds(start, end), "seconds\n")


def split_dataset(path, output_dir):
    print(fmt.WAIT_SYMBOL, "Splitting dataset ", path, "to", output_dir)
    start = timer()
    f = open(path, 'rb')

    objects = ijson.items(f, 'item')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, obj in enumerate(objects):
        path = os.path.join(output_dir, str(i) + '.json')

        with open(path, 'w') as out:
            json.dump(obj, out, indent=2)
        out.close()

    end = timer()
    print(fmt.OK_SYMBOL, "Finished splitting. Took",
          get_elapsed_seconds(start, end), 'seconds')


@profiler.do_profile()
# TODO: Change to new file structure
def get_dataset_indexes(path, count=None):
    datasets = []
    print(fmt.WAIT_SYMBOL, "Gathering information on the dataset...")

    for f in os.listdir(path):
        if f.endswith(".json"):
            datasets.append(int(f.split('.')[0]))

    if count:
        return random.sample(datasets, count)
    else:
        return datasets

    """
    with open(path, 'rb') as f:
        objects = ijson.items(f, 'item')
        num_objects = sum(1 for _ in objects)

        if count:
            print(fmt.WAIT_SYMBOL, "Indexing", count, "random data objects...")
            for i in range(0, count):
                choice = random.randint(0, num_objects)
                selected_objects.append(choice)
        else:
            print(fmt.WAIT_SYMBOL, "Indexing dataset...")
            selected_objects.extend(range(0, num_objects))
    """


@profiler.do_profile()
def load_json(path, index=None, verbose=True):
    try:
        f = open(path, 'r')

        if verbose:
            print(fmt.WAIT_SYMBOL, 'Loading file:', path)
        try:
            start = timer()

            if index:
                objects = ijson.items(f, 'item')

                for obj in islice(objects, index, index + 1):
                    # Only loads one object always, so this is messy but works
                    json_data = obj

            else:
                json_data = json.load(f)
            end = timer()

            if verbose:
                print(fmt.OK_SYMBOL, 'Loaded. Took:', get_elapsed_seconds(start, end), "seconds")
        except (ValueError) as error:
            print(error)
            return None
        f.close()
        return json_data
    except (IOError) as error:
        print(error)
        return None

# TODO: There is probably a better way to get from json to a defaultdict,
# but this works..


def json_to_defaultdict(json_str):
    def_dict = defaultdict(list)

    print(fmt.WAIT_SYMBOL, 'Converting JSON to Dict...')
    start = timer()
    for key in json_str:
        dict_key = get_key(key)

        for element in json_str[key]:
            def_dict[dict_key].append(element)
    end = timer()
    print(fmt.OK_SYMBOL, "Done. Took: ",
          get_elapsed_seconds(start, end), "seconds\n")
    return def_dict
