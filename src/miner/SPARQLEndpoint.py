from SPARQLWrapper import SPARQLWrapper
from rdflib import py3compat as compat
import constants as c, formatting as fmt
from timeit import default_timer as timer
from timing import get_elapsed_seconds
import subprocess

class SparqlServer(object):
    def __init__(self, start_server=True):
        self.sparql = SPARQLWrapper(c.SPARQL_ENDPOINT)
        if start_server:
            subprocess.Popen(c.SERVER_START, shell=True)

    def import_graph(self, graph):
        print (fmt.WAIT_SYMBOL, "Importing graph to", c.SPARQL_ENDPOINT)
        start = timer()
        gs = graph.serialize(format='nt')
        query_string = gs.decode('utf-8')
        self.sparql.setQuery('INSERT DATA { %s }' %  query_string)
        self.sparql.method = 'POST'
        self.sparql.query()
        end = timer()
        print (fmt.OK_SYMBOL, "Import complete. Took", get_elapsed_seconds(start, end), "seconds")

    def import_dataset(self, dataset):
        print (fmt.WAIT_SYMBOL, "Importing dataset to", c.SPARQL_ENDPOINT)
        start = timer()
        ds = dataset.serialize(format='turtle')
        query_string = ds.decode('utf-8')
        self.sparql.setQuery('INSERT DATA { %s }' % query_string)
        self.sparql.method = 'POST'
        self.sparql.query()
        end = timer()
        print (fmt.OK_SYMBOL, "Import complete. Took", get_elapsed_seconds(start, end), "seconds")
