"""
API for processing comtrade data
"""

import networkx as nx
import os
import pickle
import xml.etree.ElementTree as ET
from collections import OrderedDict

# Flow codes
# ----------
FLOW_IMPORT = '1'
FLOW_EXPORT = '2'
FLOW_REEXPORT = '3'
FLOW_REIMPORT = '4'

def read_country_data(path):
    """
    Return an `OrderedDict` that maps Comtrade country codes to
    country names. This should be passed to `load_from_xml`.

    Country code XML: http://bit.ly/RpP2Aq

    :param path: Comtrade list of country names (XML)
    """
    returned = OrderedDict()
    with open(path, 'r') as f:
        xml = ET.fromstring(f.read())
        for row in xml.findall('r'):
            d = {}
            for el in row:
                d[el.tag] = el.text
            returned[d['code']] = d['name']
    return returned

def read_commodity_data(path):
    """
    Return an `OrderedDict` that maps Comtrade commodity codes to
    commodity descriptions.

    Commodity code XML is at [1], where `px` is the classification scheme
    and `cc` controls the types of codes returned.

    [1] http://comtrade.un.org/ws/refs/getCommodityList.aspx?px=H1&cc=??

    :param path: Comtrade list of commodity names (XML)
    """
    returned = OrderedDict()
    with open(path, 'r') as f:
        xml = ET.fromstring(f.read())
        for row in xml.findall('r'):
            d = {}
            for el in row:
                d[el.tag] = el.text
            returned[d['code']] = d['descE']
    return returned

def load_from_xml(path, country_data, commodity_data = None):
    """
    Returns a dict with the following structure:

    'commodity': the given commodity, as a string
    'commodity_code': Comtrade ID for the given commodity
    'year': the given year, as a string
    'countries': list of strings for all countries in the network.
    'data': matrix of size n x n, where `n = len(countries)`.

    :param path: path to XML Comtrade file
    :param country_data: Comtrade country map from `read_country_data`
    """
    # Sample Comtrade row:
    #    <r>
    #        <pfCode>H0</pfCode>                  # Classification scheme
    #        <yr>1990</yr>                        # Data year
    #        <rgCode>1</rgCode>                   # Flow code
    #        <rtCode>36</rtCode>                  # Reporting country
    #        <ptCode>0</ptCode>                   # Partner country
    #        <cmdCode>27</cmdCode>                # Commodity code
    #        <cmdID>1088</cmdID>
    #        <qtCode>1</qtCode>
    #        <TradeQuantity/>
    #        <NetWeight/>
    #        <TradeValue>2188359804</TradeValue>  # Amount traded
    #        <estCode>0</estCode>
    #        <htCode>1</htCode>
    #    </r>
    commodity = commodity_code = year = None
    g = nx.DiGraph()
    g.add_nodes_from(country_data.values())

    with open(path, 'r') as f:
        xml = ET.fromstring(f.read())
        edges = []
        for row in xml.findall('r'):
            row_data = {}
            for el in row:
                row_data[el.tag] = el.text

            year = row_data['yr']
            commodity_code = row_data['cmdCode']
            value = row_data['TradeValue']
            flow_direction = row_data['rgCode']
            reporter = row_data['rtCode']
            partner = row_data['ptCode']

            if flow_direction == FLOW_EXPORT:
                importer = country_data[reporter]
                exporter = country_data[partner]
                edges.append((importer, exporter, int(value)))

        g.add_weighted_edges_from(edges)
        g.graph.update({'year': year,
                        'commodity_code': commodity_code})
        if commodity_data is not None:
            g.graph['commodity'] = commodity_data[commodity_code]
        return g

if __name__ == '__main__':
    import os
    comtrade_country_xml = os.path.expanduser('~/projects/itn/metadata/comtrade_countries.xml')
    comtrade_file = os.path.expanduser('~/projects/itn/data/comtrade/27_1990.xml')
    load_from_xml(comtrade_file, read_country_data(comtrade_country_xml))
