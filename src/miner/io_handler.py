import json as json
from collections import defaultdict
from timeit import default_timer as timer
from timing import get_elapsed_seconds
import formatting as fmt

def save_dataset(filename, dataset):
    with open(filename, 'wb') as f:
        print (fmt.WAIT_SYMBOL, 'Saving:', filename)
        start = timer()
        dataset.serialize(f, format='turtle')
        end = timer()
    print (fmt.OK_SYMBOL, 'Saved. Took:', get_elapsed_seconds(start, end), "seconds\n")

def save_graph(filename, graph):
    with open(filename, 'wb') as f:
        print (fmt.WAIT_SYMBOL, 'Saving:', filename)
        start = timer()
        graph.serialize(f, format='nt')
        end = timer()
    print (fmt.OK_SYMBOL, 'Saved. Took:', get_elapsed_seconds(start, end), "seconds\n")

def save_json(filename, data):
    with open(filename, 'w') as f:
        print (fmt.WAIT_SYMBOL, 'Saving:', filename)
        start = timer()
        json.dump(data, f)
        end = timer()
    print (fmt.OK_SYMBOL, 'Saved. Took:', get_elapsed_seconds(start, end), "seconds\n")


def load_json(path):
    try:
        f = open(path, 'r')
        print (fmt.WAIT_SYMBOL, 'Loading file:', path)
        try:
            start = timer()
            json_data = json.load(f)
            end = timer()
            print (fmt.OK_SYMBOL, 'Loaded. Took:', get_elapsed_seconds(start, end), "seconds")
        except (ValueError) as error:
            print (error)
            return None
        f.close()
        return json_data
    except (IOError) as error:
        print (error)
        return None

# TODO: There is probably a better way to get from json to a defaultdict, but this works..
def json_to_defaultdict(json_str):
    def_dict = defaultdict(list)

    print (fmt.WAIT_SYMBOL, 'Converting JSON to Dict...')
    start = timer()
    for key in json_str:
        for element in json_str[key]:
            def_dict[str(key)].append(element)
    end = timer()
    print (fmt.OK_SYMBOL, "Done. Took: ", get_elapsed_seconds(start, end), "seconds\n")
    return def_dict
