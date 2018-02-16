from SPARQLWrapper import SPARQLWrapper, BASIC, URLENCODED, POSTDIRECTLY
import constants as c
import formatting as fmt
from timeit import default_timer as timer
from timing_handler import get_elapsed_seconds
import urllib


class SparqlServer(object):
    def __init__(self, endpoint_url, username=None, password=None, ):
        self.username = username
        self.password = password
        self.sparql = SPARQLWrapper(endpoint_url)

    def __query__(self, http_method, request_method, query_string):
        if self.username and self.password:
            self.sparql.setHTTPAuth(BASIC)
            self.sparql.setCredentials(self.username, self.password)

        self.sparql.setQuery('INSERT DATA { %s }' % query_string)
        self.sparql.setRequestMethod(request_method)
        self.sparql.method = http_method
        self.sparql.setReturnFormat('json')

        try:
            self.sparql.query()
            return True
        except urllib.error.URLError as e:
            if hasattr(e, 'code'):
                if e.code == 404:
                    print('404 Error: Endpoint not found')
                elif e.code == 401:
                    print('401 Error: Unauthorized access to endpoint')
                elif e.code == 400:
                    print('400 Error: ')
                else:
                    print('HTTP Error:', e)
            else:
                print('Error:', e)

            return False
        except Exception as e:
            print('Error:', e)
            return False

    def put(self, query_string, post_directly=True):
        if post_directly:
            request_method = POSTDIRECTLY
        else:
            request_method = URLENCODED

        return self.__query__("PUT", request_method, query_string)

    def post(self, query_string, post_directly=True):
        if post_directly:
            request_method = POSTDIRECTLY
        else:
            request_method = URLENCODED

        return self.__query__("POST", request_method, query_string)

    def import_graph(self, graph, format_type='turtle'):
        print(fmt.WAIT_SYMBOL, "Importing graph to", c.SPARQL_ENDPOINT)
        start = timer()
        gs = graph.serialize(format=format_type)
        query_string = gs.decode('utf-8')

        if self.post(query_string):
            end = timer()
            print(fmt.OK_SYMBOL, "Import complete. Took",
                  get_elapsed_seconds(start, end), "seconds")

            return True
        else:
            print(fmt.ERROR_SYMBOL, "Import failed.")
            return False

    def import_dataset(self, dataset, format_type='turtle'):
        print(fmt.WAIT_SYMBOL, "Importing dataset to", c.SPARQL_ENDPOINT)
        start = timer()
        ds = dataset.serialize(format=format_type)
        query_string = ds.decode('utf-8')

        if self.post(query_string):
            end = timer()
            print(fmt.OK_SYMBOL, "Import complete. Took", get_elapsed_seconds(start, end), "seconds")
            return True
        else:
            return False
