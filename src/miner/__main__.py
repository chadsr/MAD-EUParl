from rdflib import Dataset
import argparse

import constants as c, main as m, save as s, downloader as dl

print ("Data directory:", c.DATA_DIR)

parser = argparse.ArgumentParser()
parser.add_argument("--update", help="Will fetch the latest dataset and then run", action="store_true")
args = parser.parse_args()

if args.update:
    print ("Downloading latest datasets...")
    dl.download_datasets()
else:
    print ("Using existing datasets")

ds = Dataset()
ds.bind(c.PREFIX, c.ONT)
ds.bind('dbo', c.DBO)
ds.bind('dbr', c.DBR)
ds.bind('dbp', c.DBP)
ds.bind('foaf', c.FOAF)

graph = ds.graph(c.ONT)
ds, graph = m.convert_mep(c.DATA_MEP, ds, graph)

print ("Saving JSON Dumps...")
s.save_json(c.DICT_MEPS, m.dict_mep)
s.save_json(c.DICT_PARTIES, m.dict_party)

ds, graph = m.convert_dossier(c.DATA_DOSSIER, ds, graph)

ds, graph = m.convert_votes(c.DATA_VOTES, ds, graph)

print ("Saving Dataset...")
s.save_dataset(c.DATA_OUTPUT, ds)
