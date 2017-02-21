import tarfile
import urllib.request
from urllib2 import URLError, urlopen
from urlparse import urlparse
from os.path import basename
import os, datetime, time

import constants as c

def download_datasets():

    for url in c.DATA_URLS:
        uo = urlopen(url)
        meta = uo.info()
        modified_date = meta.getheaders("Last-Modified")

        print modified_date
        modified_remote = time.mktime(datetime.datetime.strptime(modified_date, '%a, %d %b %Y %X UTC').timetuple())
        print modified_remote

        disassembled = urlparse(url)
        file_name = basename(disassembled.path)
        path = c.JSON_DIR + file_name

        if os.path.getmtime(path) > modified_remote:
            try:
                print ("Downloading", url, "to", path, "...")
                urllib.request.urlretrieve(url, path)
                print ("Extracting dataset...")
                extract_dataset(path)
            except URLError, e:
                if e.code = 404:
                    print ("Resource", url, "could not be found")
                else:
                    print ("%s" % e)
        else:
            print (file_name, "already the latest version. skipping.")

def extract_dataset(path):
    with tarfile.open(path) as f:
        f.extractall('.')
