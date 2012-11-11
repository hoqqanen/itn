import networkx as nx
from utils import get_graph, read, convert_country_code, ct_to_wb, check_path, write
import operator
import numpy as np
import matplotlib.pyplot as plt
import csv

###Special Utility
def feature_reformat(featureData):
  """
  Reformats featureData[year] type to be a dictionary 
  {country:{feature:value}} instead of {feature:{country:value}}
  """
  formatted = {}
  for f in featureData:
    for country in featureData[f]:
      try:
        formatted[country].append(featureData[f][country])
      except KeyError: 
        formatted[country] = []
        formatted[country].append(featureData[f][country])
      except TypeError:
        print 'SOMETHING WENT BONK!'
  return formatted


###Export features to CSV
def f_to_csv(featureData,filepath,year):
  """
  Takes featureData as returned by feature_extraction and a featureDict
  and formats rows = country codes, columns = feature values
  with a header by featureData keys
  """
  fkeys = ['country code']
  for f in featureData:
    fkeys.append(f)
  formatted = feature_reformat(featureData)
  formattedAgain = [] #Turn it from a dictionary into a list
  for c in formatted:
    boo = [c]
    boo.extend(formatted[c])
    formattedAgain.append(boo)

  check_path(filepath)
  with open(filepath+year+'.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(fkeys)
    writer.writerows(formattedAgain)
  return True


###Feature Functions all have type signature G -> dict of {countryCodes: values}
def f_macro(G,fn):
  """
  A special feature extraction utility function that takes 
  a graph and a lambda fn which has signature G,n -> val.
  """
  return dict(zip(G.nodes(),map(lambda n:fn(G,n),G.nodes())))

def f_pagerank(G,year=False):
  return nx.pagerank(G)

def f_degree(G,year=False):
  return f_macro(G,lambda G,n: G.degree(n))

def f_weight_sum(G,year=False):
  fDat = {}
  for country in G.nodes():
    E = G.edges(country,data=True)
    fDat[country] = sum(map(lambda x: x[2]['weight'], E))
  return fDat

def f_reverse_weight_sum(G,year=False):
  return f_weight_sum(G.reverse(copy=True))

def f_triangles(G,year=False):
  return f_macro(G.to_undirected(),lambda G, n: nx.triangles(G,n))

def f_clustering(G,year=False):
  return f_macro(G.to_undirected(),lambda G, n: nx.clustering(G,n,'weight'))

def f_gdp_abs(G,year):
  return f_macro(G, lambda G, n: G.node[n]['gdp'])

def f_gdp_rank(G,year):
  absGDP = f_gdp_abs(G,year)
  sortedTuples = sorted(absGDP.iteritems(), key=operator.itemgetter(1), reverse=True)
  fDat = {}
  rank = 1
  for e in sortedTuples:
    fDat[e[0]] = rank
    rank += 1
  return fDat



###Extraction Code
def feature_extraction(years,featureDict):
  """
  Saves pickle of and returns an dict of feature dicts in the form
        {year:{featureName:{countryCode:featureValue}}}
  :param years: a list e.g. range(1980,2000)
  :param featureDict: a dictionary of features in the form
                    {featureName:featureFunction}
                    featureName is a string
                    featureFunction: takes a graph (and possibly a year) 
                        and outputs a dictionary {node:featureValue}
  """
  featureData = {}
  for year in years:
    print year
    G = get_graph(year,'essex')
    featureData[year] = {}
    for f in featureDict:
      featureData[year][f] = featureDict[f](G,year)
    write(featureData[year],'data/raw/essex/features/pickle/',str(year))
    f_to_csv(featureData[year],'data/raw/essex/features/csv/',str(year))
  return featureData

if __name__ == '__main__':
  years = range(2000,2001)
  featureDict = {'pagerank':f_pagerank, \
    'degree':f_degree, \
    'weighted edge out sum':f_weight_sum, \
    'weighted edge in sum':f_reverse_weight_sum, \
    'number of triangles': f_triangles, \
    'absolute gdp': f_gdp_abs, \
    'gdp rank': f_gdp_rank, \
    'clustering': f_clustering}
  featureData = feature_extraction(years,featureDict)
  
