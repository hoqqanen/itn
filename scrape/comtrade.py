"""
    scrape.comtrade
    ~~~~~~~~~~~~~~~
    This script is used to grab data from the comtrade database. For help in
    using this data, see `api.comtrade`.
"""

import threading
import time
import urllib as U
import xml.etree.ElementTree as ET

# Query information
GET_URL = 'http://comtrade.un.org/ws/get.aspx'
DB_QUERY_URL = 'http://comtrade.un.org/db/dqBasicQueryResultsd.aspx?action=csv&cc=TOTAL&px=H2&r=372&y=2006'

# String encoding for Boolean parameters
QUERY_TRUE = 'true'
QUERY_FALSE = 'false'

# Commodity schemes
SCHEME_SITC = 'S1'
SCHEME_HS = 'HS'

# Commodity codes
FUEL_AND_OIL = 27
PHARMACEUTICALS = 30

YEARS = range(1962, 2011 + 1)

class ComtradeThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            (url, outfile) = self.queue.get()
            print url, ': (%s)' % self.getName()
            U.urlretrieve(url, outfile)
            self.queue.task_done()


def prepare(**kw):
    """
    Construct a query URL and the name of the output file.

    Paremeters are listed at http://bitly.com/T7pWCH. The most useful are:
    
      - cc: commodity code. See commodity code list [1] or pass 'TOTAL'
            to get the total.
            [1] http://comtrade.un.org/db/mr/rfCommoditiesList.aspx
      - comp: if True, compress the data. (TODO: how to decompress?)
      - px: classification format ('HS' is the most common)
      - r: reporting countries
      - y: 4-digit year
    """

    px = SCHEME_SITC
    cc = kw['cc']
    if px in [SCHEME_SITC]:
        cc = str(cc)
    elif px in [SCHEME_HS]:
        cc = str(cc) if int(cc) >= 10 else ('0' + str(cc))

    outfile = '/host/Users/Arun/Documents/ITN/{0}_{1}_{2}.xml'.format(px, kw['cc'], kw['y'])

    default = kw.setdefault
    default('comp', QUERY_FALSE)
    default('px', px)

    query_string = U.urlencode(kw)
    url = GET_URL + "?" + query_string

    return url, outfile

if __name__ == '__main__':
    import sys
    import Queue
    queue = Queue.Queue()

    # Populate queue
    for cc in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        for y in YEARS:
            url, outfile = prepare(**{'cc': cc, 'y': y})
            queue.put((url, outfile))

    for i in range(7):
        t = ComtradeThread(queue)
        t.setDaemon(True)
        t.start()

    queue.join()
