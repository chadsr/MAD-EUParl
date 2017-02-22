from rdflib import Dataset
import argparse
from timeit import default_timer as timer
from timing import get_elapsed_seconds

import constants as c, main as m, io_handler as io, downloader as dl, formatting as fmt

print (fmt.INFO_SYMBOL, "Data directory:", c.DATA_DIR, "\n")

parser = argparse.ArgumentParser()
parser.add_argument("--update", help="Will fetch the latest dataset and then run", action="store_true")
args = parser.parse_args()

start = timer()

if args.update:
    print (fmt.WAIT_SYMBOL, "Downloading latest datasets...")
    dl.download_datasets()
else:
    print (fmt. WARNING_SYMBOL, "Using existing datasets")

ds = Dataset()
ds.bind(c.PREFIX, c.ONT)
ds.bind('dbo', c.DBO)
ds.bind('dbr', c.DBR)
ds.bind('dbp', c.DBP)
ds.bind('foaf', c.FOAF)

graph = ds.graph(c.ONT)
ds, graph = m.convert_mep(c.DATA_MEP, ds, graph)

io.save_json(c.DICT_MEPS, m.dict_mep)
io.save_json(c.DICT_PARTIES, m.dict_party)

ds, graph = m.convert_dossier(c.DATA_DOSSIER, ds, graph)
ds, graph = m.convert_votes(c.DATA_VOTES, ds, graph)

io.save_dataset(c.DATA_OUTPUT, ds)

end = timer()

print (fmt.INFO_SYMBOL ,"Total execution time:", get_elapsed_seconds(start, end), "seconds")
