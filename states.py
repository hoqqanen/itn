import csv
import os
from collections import Counter

import networkx as nx

# Commodity codes (format: SCTG)
CODES = [
    # '00',  # ???????????????????????????
    '01',  # live animals and fish
    '02',  # cereal grains
    '03',  # other agricultural products (except for animal feed)
    '04',  # animal feed and producs of animal origin (nec)
    '05',  # meat, fish, seafood
    '06',  # milled grain products
    '07',  # other prepared foodstuffs
    '08',  # alcoholic beverages
    '09',  # tobacco products
    '10',  # monumental or building stone
    '11',  # natural sands
    '12',  # gravel and crused stone
    '13',  # Non-metallic minerals
    '14',  # metallic ores and concentrates
    '15',  # coal
    '17',  # gasoline and turbine fuel
    '18',  # fuel oils
    '19',  # coal and petroleum products (nec)
    '20',  # basic chemicals
    '21',  # pharma
    '22',  # fertilizers
    '23',  # chemical products
    '24',  # plastics and rubber
    '25',  # logs and other rough wood
    '26',  # wood products
    '27',  # pulp, newsprint, paper, paperboard
    '28',  # paper or paperboard articles
    '29',  # printed products
    '30',  # textiles, leather, and articles of textiles or leather
    '31',  # non-metallic mineral products
    '32',  # base metal in primary or semi-finished forms
    '33',  # articles of base metal
    '34',  # machinery
    '35',  # electronic and other electrical equipment
    '36',  # motorized and other vehicles, including parts
    '37',  # transportation equipment (nec)
    '38',  # precision instruments
    '39',  # Furniture, mattresses, lamps, signs
    '40',  # Miscellaneous manufactured
    '41',  # Waste and scrap
    '43',  # Mixed freight
    '99'   # Other, miscellaneous
]


FIELDS = ['source_state', 'source_region', 'dest_state', 'dest_region',
         'commodity', 'commodity_name',
         'value', 'tons', 'ton_miles',

         # "Coefficient of variation"; not sure how to use these
         'value_cv', 'tons_cv', 'ton_miles_cv']


def data(filename, code, src_key, dest_key, value_key):
    """Gather data by commodity code. Use `data_by_state` and
    `data_by_region` instead.

    :param code: the code to use.
    """
    counts = Counter()
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, fieldnames=FIELDS)
        next(reader)
        for row in reader:
            source = row[src_key]
            dest = row[dest_key]
            value = row[value_key]
            commodity = row['commodity']

            if commodity == code:
                # TODO: find out what S and Z stand for
                if value in 'SZ':
                    continue

                # US overall
                if source == '-' or dest == '-':
                    continue

                key = (source, dest)
                counts[key] += int(value)
    return counts


def data_by_state(filename, code, value_key='value'):
    """Pairwise trade for 51 states (50 + DC)

    :param filename: path to commodities file
    :param code: commodity code
    """
    return data(filename=filename, code=code,
                src_key='source_state', dest_key='dest_state',
                value_key=value_key)


def data_by_region(filename, code, value_key='value'):
    """Pairwise trade for 159 sub-state regions

    :param filename: path to commodities file
    :param code: commodity code
    """
    return data(filename=filename, code=code,
                src_key='source_region', dest_key='dest_region',
                value_key=value_key)


def get_graph_from_counter(counts):
    """Generate a graph from some `dict`, such as the one returned by
    `statewise_data`.

    :param counts: a `dict` mapping (src, dest) tuples to weights
    """
    g = nx.DiGraph()
    for k in counts:
        src, dest = k
        weight = counts[k]
        g.add_edge(src, dest, weight=weight)
    return g


if __name__ == '__main__':
    """Make a graph and print some stats"""
    filename = os.path.expanduser('~/Downloads/survey/commodity.csv')
    counter = data_by_region(filename=filename, code='00')
    g = get_graph_from_counter(counter)

    print 'Nodes: ', len(g.nodes())
    print 'Edges: ', len(g.edges())
    print

    s = 'List of nodes'
    print s
    print '=' * len(s)

    for n in sorted(g.nodes()):
        print ' ', n
