from SPARQLWrapper import SPARQLWrapper
from rdflib import py3compat as compat
import constants as c
import formatting as fmt
from timeit import default_timer as timer
from timing_handler import get_elapsed_seconds
import subprocess


class SparqlServer(object):
    def __init__(self, start_server=True):
        self.sparql = SPARQLWrapper(c.SPARQL_ENDPOINT)

        if start_server:
            subprocess.Popen(c.SERVER_START, shell=True)
            subprocess.Popen(c.SERVER_IMPORT_ONT, shell=True)

    def postQuery(self, query_string):
        self.sparql.setQuery('INSERT DATA { %s }' % query_string)
        self.sparql.method = 'POST'

        try:
            self.sparql.query()
        except (error.URLError) as e:
            if e.code == 404:
                print('404 Error whilst connecting to endpoint')
            elif e.code == 401:
                print('401 Error: Unauthorized access to endpoint')
            else:
                print('Error:', e)

    def import_graph(self, graph):
        print(fmt.WAIT_SYMBOL, "Importing graph to", c.SPARQL_ENDPOINT)
        start = timer()
        gs = graph.serialize(format='nt')
        query_string = gs.decode('utf-8')

        self.postQuery(query_string)

        end = timer()
        print(fmt.OK_SYMBOL, "Import complete. Took",
              get_elapsed_seconds(start, end), "seconds")

    def import_dataset(self, dataset):
        # print (fmt.WAIT_SYMBOL, "Importing dataset to", c.SPARQL_ENDPOINT)
        # start = timer()
        ds = dataset.serialize(format='turtle')
        query_string = ds.decode('utf-8')

        self.postQuery(query_string)
        # end = timer()
        # sprint (fmt.OK_SYMBOL, "Import complete. Took", get_elapsed_seconds(start, end), "seconds")
