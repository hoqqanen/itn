"""
Comtrade scraper
================
"""

import time
import urllib as U
import xml.etree.ElementTree as ET

# Query information
GET_URL = 'http://comtrade.un.org/ws/get.aspx'
DB_QUERY_URL = 'http://comtrade.un.org/db/dqBasicQueryResultsd.aspx?action=csv&cc=TOTAL&px=H2&r=372&y=2006'

# String encoding for Boolean parameters
QUERY_TRUE = 'true'
QUERY_FALSE = 'false'

# Commodity codes
FUEL_AND_OIL = 27
PHARMACEUTICALS = 30

YEARS = range(1962, 2011 + 1)

def scrape(**kw):
    """
    Scrape the Comtrade database.
    
    Paremeters are listed at http://bitly.com/T7pWCH. The most useful are:
    
      - cc: commodity code. See commodity code list [1] or pass 'TOTAL'
            to get the total.
            [1] http://comtrade.un.org/db/mr/rfCommoditiesList.aspx
      - comp: if True, compress the data. (TODO: how to decompress?)
      - px: classification format ('HS' is the most common)
      - r: reporting countries
      - y: 4-digit year
    """

    outfile = 'data/{0}_{1}.xml'.format(kw['cc'], kw['y']) 
    default = kw.setdefault
    default('comp', QUERY_FALSE)
    default('px', 'HS')

    query_string = U.urlencode(kw)
    url = GET_URL + "?" + query_string

    print url, ':',
    start = time.time()
    response = U.urlretrieve(url, outfile)
    stop = time.time()
    print ' [{0} sec]'.format(stop - start)

if __name__ == '__main__':
    import sys
    for cc in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        cc = str(cc) if int(cc) >= 10 else ('0' + str(cc))
        for y in YEARS:
            scrape(**{'cc': cc, 'y': y})
