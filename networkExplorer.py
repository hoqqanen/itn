import api.comtrade as ct
import networkx as nx
import os
import pickle
import matplotlib
from utils import checkpath, write, plot_distribution, degree_distribution

def getGraph(year,resource):
  comtrade_country_xml = 'data/raw/comtrade/metadata/countries.xml'
  comtrade_file = 'data/raw/comtrade/'+resource[0]+'/'+resource[1]+'_'+str(year)+'.xml'
  G = ct.load_from_xml(comtrade_file, ct.read_country_data(comtrade_country_xml))
  return G

def linksAddedPerYear(years,resource):
  #predicates = list of pairs of lambda expressions returning true/false
  predicates = [[lambda x: x[2]['weight']>0, lambda x: x[2]['weight']>0],[lambda x: x[2]['weight']>100000, lambda x: x[2]['weight']>200000]]
  links = {}
  for y in years[0:-2]:
    [G1,G2] = [getGraph(y,resource),getGraph(y+1,resource)]
    [E1,E2] = [G1.edges(data=True),G2.edges(data=True)]
    #print [len(E1),len(G1.nodes()),len(E1)/(float(len(G1.nodes()))*len(G1.nodes()))]
    links[y] = {}
    counter = 0
    for p in predicates:
      counter += 1
      [newE1, newE2] = [filter(p[0],E1),filter(p[1],E2)]
      newE1simple = map(lambda x: (x[0],x[1]), newE1)
      #addedEdges = [x in newE2 if (x[0],x[1]) not in newE1simple]
      addedEdges = filter(lambda x: (x[0],x[1]) not in newE1simple, newE2)
      links[y][counter] = addedEdges
      print [y, counter, len(addedEdges)]
  return links

#Remains to be done: degree distribution network images... etc.

def linkRatio(years,resource):
  return 0

def graphImage(years,rname,resource):
  for year in years:
    G = getGraph(year,resource)
    items = degree_distribution(G)
    directory = 'data/raw/comtrade/explore/images/'
    title = rname+' deg dist year'+str(year)
    plot_distribution([k for (k,v) in items], [v for (k,v) in items], directory, title)
  return 0

if __name__ == '__main__':
  years = range(1988,2012)
  resources = {'fuel':['fuelOil19882011','27']}
  for r in resources:
    resource = resources[r]
    #write(linksAddedPerYear(years,resource),'data/raw/comtrade/explore/'+resource[0],'/links')
    #write(linkRatio(years,resource),resource[0]+'/ratios')
    graphImage(years,r,resource)