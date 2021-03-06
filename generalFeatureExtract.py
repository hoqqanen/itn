import networkx as nx
from utils import get_graph, read, convert_country_code, ct_to_wb, check_path, write, get_subgraph
import operator
import numpy as np
import matplotlib.pyplot as plt
import csv
import copy

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
    boo = [c.encode('ascii', 'ignore')]
    boo.extend(map(lambda x: x if type(x)!=type(' ') else x.encode('ascii', 'ignore'), formatted[c]))
    formattedAgain.append(boo)

  check_path(filepath)
  with open(filepath+year+'.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(fkeys)
    writer.writerows(formattedAgain)
  return True



def f_export(G, countries, year):
  expDat={}
  for c1 in countries:
    for c2 in countries:
      try:
        exp=G[c1][c2]["weight"]
      except:
        exp=0
      expDat[(c1, c2)]=exp
  return expDat

def f_export_diff(G1, countries, year):
  expDiffDat={}
  G0=get_graph(year-1, "essex")
  for c1 in countries:
    for c2 in countries:
      try:
        exp0=G0[c1][c2]["weight"]
      except:
        exp0=0
      try:
        exp1=G1[c1][c2]["weight"]
      except:
        exp1=0
      expDiffDat[(c1, c2)]=exp1-exp0
  return expDiffDat

def f_import(G, countries, year):
  impDat={}
  for c1 in countries:
    for c2 in countries:
      try:
        imp=G[c2][c1]["weight"]
      except:
        imp=0
      impDat[(c1, c2)]=imp
  return impDat

def f_import_diff(G1, countries, year):
  impDiffDat={}
  G0=get_graph(year-1, "essex")
  for c1 in countries:
    for c2 in countries:
      try:
        imp0=G0[c2][c1]["weight"]
      except:
        imp0=0
      try:
        imp1=G1[c2][c1]["weight"]
      except:
        imp1=0
      impDiffDat[(c1, c2)]=imp1-imp0
  return impDiffDat



###Feature Functions all have type signature G -> dict of {countryCodes: values}
def f_macro(G,fn):
  """
  A special feature extraction utility function that takes 
  a graph and a lambda fn which has signature G,n -> val.
  """
  return dict(zip(G.nodes(),map(lambda n:fn(G,n),G.nodes())))

def f_pagerank(G,year=False):
  return nx.pagerank(G)

def f_hits_hubs(G,year=False):
  return nx.hits_numpy(G)[0]

def f_hits_authorities(G,year=False):
  return nx.hits_numpy(G)[1]

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
  for n in G.nodes():
    print n
    print G.node[n]['gdp']
  #g = get_subgraph(get_graph(year, "essex"),countries)
  return f_macro(G, lambda G, n: G.node[n]['gdp']*G.node[n]['pop'])

def f_population(G,year):
  #g = get_subgraph(get_graph(year, "essex"),countries)
  return f_macro(G, lambda G, n: G.node[n]['pop'])

def f_gdp_rank(G,year):
  absGDP = f_gdp_abs(G,year)
  sortedTuples = sorted(absGDP.iteritems(), key=operator.itemgetter(1), reverse=True)
  fDat = {}
  rank = 1
  for e in sortedTuples:
    fDat[e[0]] = rank
    rank += 1
  return fDat

nodefeatureDict = {'gdp rank': f_gdp_rank, \
    'absolute gdp': f_gdp_abs, \
    'population': f_population, \
    'pagerank':f_pagerank, \
    'degree':f_degree, \
    'weighted edge out sum':f_weight_sum, \
    'weighted edge in sum':f_reverse_weight_sum, \
    'number of triangles': f_triangles, \
    'clustering': f_clustering, \
    'hits hubs': f_hits_hubs, \
    'hits authorities': f_hits_authorities}

edgefeatureDict={ 'export': f_export, \
    'import': f_import, \
    'export diff': f_export_diff, \
    'import diff': f_import_diff}

def f_distance_pairs(G, year):
    """Return a dict that maps country code tuples to distance values. Since
    these values don't change over time, we can build them just once.
    """
    try:
        return f_distance_pairs.data
    except AttributeError:
        pass

    returned = {}
    with open('data/raw/distances.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            key = (line[0], line[1])  # commodity codes
            value = float(line[2])    # distance in kilometers
            returned[key] = value

    # Cache data for later calls
    f_distance_pairs.data = returned
    return returned

###Extraction Code
def node_feature_extraction(years,featureDict,resource):
  """
  Saves pickle of and returns a dict of feature dicts in the form
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
    G = get_graph(year,resource)
    G = G.subgraph(countries)
    featureData[year] = {}
    for f in featureDict:
      featureData[year][f] = featureDict[f](G,year)
    write(featureData[year],'data/raw/features/'+resource[0]+'/pickle/',str(year))
    f_to_csv(featureData[year],'data/raw/features/'+resource[0]+'/csv/',str(year))
  return featureData



###Extraction Code
def edge_feature_extraction(years, countries, featureDict, resource):
  
  featureData = {}
  for year in years:
    print year
    G = get_graph(year,resource)
    for f in featureDict:
      featureData[f+str(year)] = featureDict[f](G, countries ,year)
  return featureData



def convertNodalFeaturesToEdgeFeatures(countries,years, nodefeatureDict):
  edgeData={}
  for year in years:
    for feature in nodefeatureDict[year]:
      f1=feature+"c1"+str(year)
      f2=feature+"c2"+str(year)
      edgeData[f1]={}
      edgeData[f2]={}
      for c1 in countries:
       for c2 in countries:
          try:
            edgeData[f1][(c1, c2)]=nodefeatureDict[year][feature][c1]
            edgeData[f2][(c2, c1)]=nodefeatureDict[year][feature][c2]
          except KeyError:
            #print nodefeatureDict[year][feature]
            print [c1,c2]
            #print nodefeatureDict[year][feature]
  return edgeData

from pprint import pprint

def getEdgeFeatureCSV(years,resource):
  gs={}
  global countries
  cList =[]
  As=[]
  
  for y in years:
    gs[y]=get_graph(y, resource)
    e = get_graph(y,'essex')
    cList.append(set(gs[y].nodes()))
    cList.append(set(e.nodes()))
    #print 'For the year'
    #pprint(gs[y].nodes())
    #pprint(e.nodes())
  #pprint(cList)
  countries = list(set.intersection(*cList))
  print 'Countries included so far:'
  print countries

  edgefeatureYears=years[:-1]
  nodefeatureYear=years[-2]
  nodefeatureYears=[nodefeatureYear]

  nodefeatures=node_feature_extraction(nodefeatureYears,nodefeatureDict,resource)
  edgefeatures=edge_feature_extraction(edgefeatureYears, countries, edgefeatureDict,resource)
  nodeToEdgeFeatures=convertNodalFeaturesToEdgeFeatures(countries, nodefeatureYears, nodefeatures)
  edgefeatures.update(nodeToEdgeFeatures)

  features=edgefeatures.keys()
  check_path('data/raw/features/'+resource[0]+'/edgedata/')
  filename=open('data/raw/features/'+resource[0]+'/edgedata/'+str(years[-1])+'.csv', 'wb')
  writer = csv.writer(filename)
  fnames=copy.deepcopy(features)
  fnames.append("t")
  fnames.insert(0, "edge")
  writer.writerow(fnames)
  for c1 in countries:
    for c2 in countries:
      row=[c1+"_"+c2, ]
      for f in features:
        row.append(edgefeatures[f][(c1, c2)])
      try:
        t=gs[years[-1]][c1][c2]["weight"]
      except:
        t=0
      row.append(t)
      writer.writerow(row)




    




if __name__ == '__main__':
  years = range(1999,2001)  
  resource = ['fuelOil19882011', '27']
  print 'Doing for fuel, but nodal only. Edge is broken.'
  featureData = getEdgeFeatureCSV(years,resource)

  
