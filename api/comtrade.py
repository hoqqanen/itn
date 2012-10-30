"""
API for processing comtrade data
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy
import os
import pickle
import xml.etree.ElementTree as ET
from collections import OrderedDict

FLOW_IMPORT = '1'
FLOW_EXPORT = '2'
FLOW_REEXPORT = '3'
FLOW_REIMPORT = '4'

def read_country_data(path):
    """
    Return an `OrderedDict` that maps Comtrade country codes to
    country names.

    :param path: Comtrade list of country names (XML)
    """
    returned = OrderedDict()
    with open(path, 'r') as f:
        xml = ET.fromstring(f.read())
        for row in xml.findall('r'):
            d = {}
            for el in row:
                d[el.tag] = el.text
            returned[d['code']] = d['name']  # map code to name
    return returned

def load_from_xml(path, country_data=None):
    """
    Returns a dict with the following structure:

    'resource': the given resource, as a string
    'resource_code': Comtrade ID for the given resource
    'year': the given year, as a string
    'countries': list of strings for all countries in the network.
    'data': matrix of size n x n, where `n = len(countries)`.

    :param path: path to XML Comtrade file
    """
    # Sample Comtrade row:
    #    <r>
    #        <pfCode>H0</pfCode>
    #        <yr>1990</yr>
    #        <rgCode>1</rgCode>
    #        <rtCode>36</rtCode>
    #        <ptCode>0</ptCode>
    #        <cmdCode>27</cmdCode>
    #        <cmdID>1088</cmdID>
    #        <qtCode>1</qtCode>
    #        <TradeQuantity/>
    #        <NetWeight/>
    #        <TradeValue>2188359804</TradeValue>
    #        <estCode>0</estCode>
    #        <htCode>1</htCode>
    #    </r>
    resource = resource_code = year = None
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
            resource_code = row_data['cmdCode']  # Commodity code
            value = row_data['TradeValue']
            flow_direction = row_data['rgCode']
            reporter = row_data['rtCode']
            partner = row_data['ptCode']

            if flow_direction == FLOW_EXPORT:
                importer = country_data[reporter]
                exporter = country_data[partner]
                edges.append((importer, exporter, int(value)))

        g.add_weighted_edges_from(edges)
        return g

if __name__ == '__main__':
    import os
    comtrade_country_xml = os.path.expanduser('~/projects/itn/metadata/comtrade_countries.xml')
    comtrade_file = os.path.expanduser('~/projects/itn/data/comtrade/27_1990.xml')
    load_from_file(comtrade_file, read_country_data(comtrade_country_xml))
