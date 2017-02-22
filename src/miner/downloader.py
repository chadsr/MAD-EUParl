import lzma
from urllib import error, request, parse
from os.path import basename
import os, datetime, time

import constants as c, formatting as fmt

def download_datasets():

    for url in c.DATA_URLS:
        uo = request.urlopen(url, timeout=c.DOWNLOAD_TIMEOUT)
        modified_date = uo.headers['last-modified']
        remote_unix = time.mktime(datetime.datetime.strptime(modified_date, '%a, %d %b %Y %X GMT').timetuple())

        disassembled = parse.urlparse(url)
        file_name = basename(disassembled.path)
        path = c.JSON_DIR + file_name

        if os.path.isfile(path):
            local_unix = os.path.getmtime(path)
        else:
            local_unix = 0

        if local_unix < remote_unix:
            try:
                print (fmt.WAIT_SYMBOL, "Downloading", url, "to", path, "...")
                request.urlretrieve(url, path)
                print (fmt.WAIT_SYMBOL, "Extracting dataset...")
                extract_dataset(path)
            except (error.URLError) as e:
                if e.code == 404:
                    print (fmt.ERROR_SYMBOL, "Resource", url, "could not be found")
                else:
                    print ("%s" % e)
        else:
            print (fmt.WARNING_SYMBOL, file_name, "already the latest version. skipping.")

def extract_dataset(path):
    dir_path, filename = os.path.split(path)
    name = os.path.splitext(filename)[0]

    print (dir_path, name)

    with lzma.open(path) as f, open(c.JSON_DIR+name, 'wb') as fout:
        file_content = f.read()
        fout.write(file_content)