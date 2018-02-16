import lzma
from urllib import error, request, parse
import os
import datetime
import time
import constants as c
import formatting as fmt
from timeit import default_timer as timer
from multiprocessing import Pool

from timing_handler import get_elapsed_seconds
import io_handler as io


def __prepare_dataset__(info):
    folder, url = info
    uo = request.urlopen(url, timeout=c.DOWNLOAD_TIMEOUT)
    modified_date = uo.headers['last-modified']
    remote_unix = time.mktime(datetime.datetime.strptime(
        modified_date, '%a, %d %b %Y %X GMT').timetuple())

    disassembled = parse.urlparse(url)
    file_name = os.path.basename(disassembled.path)
    path = c.JSON_DIR + file_name

    if os.path.isfile(path):
        local_unix = os.path.getmtime(path)
    else:
        local_unix = 0

    if local_unix < remote_unix:
        try:
            print(fmt.WAIT_SYMBOL, "Downloading", url, "to", path, "...")
            request.urlretrieve(url, path)
            print(fmt.WAIT_SYMBOL, "Extracting ", path)
            start = timer()
            output_path = extract_dataset(path)
            end = timer()
            print(fmt.OK_SYMBOL, "Extracted. Took",
                  get_elapsed_seconds(start, end), 'seconds')

            io.split_dataset(output_path, folder)

            os.remove(output_path)

            return True

        except (error.URLError) as e:
            if e.code == 404:
                print(fmt.ERROR_SYMBOL, "Resource", url,
                      "could not be found")
            else:
                print("%s" % e)

            return False
    else:
        print(fmt.WARNING_SYMBOL, file_name, "already the latest version. skipping.")
        return True


def prepare_datasets(num_threads):
    if not os.path.exists(c.JSON_DIR):
        os.makedirs(c.JSON_DIR)

    num_datasets = len(c.DATA_URLS)
    if num_threads > num_datasets:
        num_threads = num_datasets

    pool = Pool(num_threads)
    pool.map(__prepare_dataset__, c.DATA_URLS.items())


def extract_dataset(path):
    dir_path, filename = os.path.split(path)
    name = os.path.splitext(filename)[0]
    output_path = os.path.join(c.JSON_DIR, name)

    with lzma.open(path) as f, open(output_path, 'wb') as fout:
        file_content = f.read()
        fout.write(file_content)
    f.close()
    fout.close()

    return output_path
