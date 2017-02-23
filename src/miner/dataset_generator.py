from rdflib import Dataset
import constants as c

class DatasetGenerator(object):
    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def get_dataset():
        ds = Dataset()
        ds.bind(c.PREFIX, c.ONT)
        ds.bind('dbo', c.DBO)
        ds.bind('dbr', c.DBR)
        ds.bind('dbp', c.DBP)
        ds.bind('foaf', c.FOAF)

        return ds
