import api.comtrade as ct
import networkx as nx
import os
import pickle
import matplotlib
import matplotlib.pyplot as plt
from utils import checkpath, read, write, plot_distribution, degree_distribution
import numpy as np

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

#Remains to be done: compute consecutive year ratios on each link
#Determine how to prune the graph//select a subset that is more meaningful
#   or do we not mind having many nodes of degree 0?
def extractLinkRatios(years,resource):
  ratios = {}
  for y in years[0:-1]:
    ratios[y] = []
    [G1,G2] = [getGraph(y,resource),getGraph(y+1,resource)]
    for e in G1.edges(data=True): #e is current year edge
      try:
        pastEdgeData = G2[e[0]][e[1]] #If it doesn't exist we except
        ratios[y].append((e[0],e[1],float(e[2]['weight'])/pastEdgeData['weight'],float(e[2]['weight']),pastEdgeData['weight']))
      except KeyError:
        bloop = 'bloop'
    #print ratios[y]
  return ratios

def graphImage(years,rname,resource):
  year = years[0]
  G = getGraph(year,resource)
  degDist = degree_distribution(G)
  print degDist #LOTS of countries with degree 0. Prune them? Pick some subset?
  directory = 'data/raw/comtrade/explore/images/'+rname
  title = rname+' deg dist year'+str(year)
  #plot_distribution([k for (k,v) in degDist], [v for (k,v) in degDist], directory+'/degDist/', str(year))
  #Visualize the network
  #ecolors = map(lambda e: e[2]['weight'], G.edges(data=True))
  pos=nx.spring_layout(G)
  nx.draw(G,pos=pos,node_size=80,with_labels=True)
  #plt.savefig(directory+'pos_influence_graph.png')
  plt.show()
  return 0

def linkRatioStats(filepath):
  yearlyRatios = read(filepath)
  means = []
  for year in yearlyRatios:
    filteredData = filter(lambda x: x[3]>100 and x[4]>100, yearlyRatios[year])
    dataList = map(lambda x: x[2], filteredData)
    #print filter(lambda y: (y[1]=='USA' or y[0]=='USA'), sorted(yearlyRatios[year], key=lambda x: x[2]))
    means.append(round(np.mean(dataList)))
  print means
  print np.mean(means)
  return 0

if __name__ == '__main__':
  years = range(1988,2012)
  resources = {'fuel':['fuelOil19882011','27']}
  for r in resources:
    resource = resources[r]
    #write(linksAddedPerYear(years,resource),'data/raw/comtrade/explore/'+resource[0],'/links')
    #write(extractLinkRatios(years,resource),'data/raw/comtrade/explore/'+resource[0],'/ratios')
    #linkRatioStats('data/raw/comtrade/explore/'+resource[0]+'/ratios')
    graphImage(years,r,resource)
