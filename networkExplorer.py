import api.comtrade as ct
import networkx as nx
import os
import pickle
import matplotlib
import matplotlib.pyplot as plt
from utils import checkpath, read, write, prune_countries, plot_distribution, degree_distribution
import numpy as np
#Foopa
def getGraph(year,resource):
  try:
    G = read('data/raw/comtrade/data/'+resource[0]+'/pickles/'+str(year))
  except IOError:
    comtrade_country_xml = 'data/raw/comtrade/metadata/countries.xml'
    comtrade_file = 'data/raw/comtrade/data/'+resource[0]+'/'+resource[1]+'_'+str(year)+'.xml'
    G = ct.load_from_xml(comtrade_file, ct.read_country_data(comtrade_country_xml))
    write(G,'data/raw/comtrade/data/'+resource[0]+'/pickles/',str(year))
  #G = prune_countries(G) Broken at the moment.
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



def p_newEdge_degree(years,resource):
  #predicates = list of pairs of lambda expressions returning true/false
  p = [lambda x: x[2]['weight']>0, lambda x: x[2]['weight']>0]
  toCounts=[]
  fromCounts=[]
  for y in years[0:-2]:
    [G1,G2] = [getGraph(y,resource),getGraph(y+1,resource)]
    [E1,E2] = [G1.edges(data=True),G2.edges(data=True)]
    [newE1, newE2] = [filter(p[0],E1),filter(p[1],E2)]
    newE1simple = map(lambda x: (x[0],x[1]), newE1)
    addedEdges = filter(lambda x: (x[0],x[1]) not in newE1simple, newE2)
    print len(addedEdges)
    for e in addedEdges:
      toCounts.append(len(G1[e[1]]))
      fromCounts.append(len(G1[e[0]]))

  plt.hist(toCounts, normed=True)
  plt.title("P(linked to| new edge")
  plt.show()
  plt.hist(fromCounts, normed=True)
  plt.title("P(linked from | new edge")
  plt.show()


def SampledDiameter(g):
  ns=sample(g.nodes(), 100)
  pathLengths=[]
  for n in ns:
    paths=nx.single_source_shortest_path(g, n)
    pathLengths.extend([len(paths[n]) for n in paths.keys()])
  return max(pathLengths)

def macroEvolution(years, resource):
  densities=[]
  diameters=[]
  for y in years:
    g=getGraph(y,resource)
    densities.append(len(g.edges())/float(len(g.nodes())))
    diameters.append(SampledDiameter(g))
  plt.plot(years, densities)
  plt.title("Density Evolution")
  plt.show()
  plt.plot(years, diameters)
  plt.title("Diameter Evolution")
  plt.show()


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
  for year in years:
    G = getGraph(year,resource)
    degDist = degree_distribution(G)
    print degDist #LOTS of countries with degree 0. Prune them? Pick some subset?
    directory = 'data/raw/comtrade/explore/'+resource[0]+'/images/'+rname
    title = rname+' deg dist year'+str(year)
    plot_distribution([k for (k,v) in degDist], [v for (k,v) in degDist], directory+'/degDist/', str(year))
  #Visualize the network
  #ecolors = map(lambda e: e[2]['weight'], G.edges(data=True))
  #pos=nx.spring_layout(G)
  #nx.draw(G,pos=pos,node_size=80,with_labels=True)
  #plt.savefig(directory+'pos_influence_graph.png')
  #plt.show()
  return 0

def linkRatioStats(filepath):
  yearlyRatios = read(filepath)
  means = []
  for year in yearlyRatios:
    if int(year)>2009:
      filteredData = filter(lambda x: x[3]>100 and x[4]>100, yearlyRatios[year])
      # the histogram of trade
      plt.figure()
      ratioData=map(lambda x: x[2], filteredData)
      bins=np.arange(0, 3, 0.01)
      hist=np.histogram(ratioData, density=True, bins=bins)[0]
      #n, bins, patches = plt.hist(ratioData, normed=1, facecolor='green', alpha=0.75, bins=np.arange(0, 3, 0.01))
      plt.loglog(bins[1:],hist,'r', marker='o')
      plt.xlabel('Ratio')
      plt.ylabel('Probability')
      plt.title("Ratio Distribution"+str(year))
      plt.show()

      plt.figure()
      ratioData=map(lambda x: x[4], filteredData)
      bins=range(0, 1000000000, 10000000)
      hist=np.histogram(ratioData, density=True, bins=bins)[0]
      #n, bins, patches = plt.hist(map(lambda x: x[4], filteredData), normed=1, facecolor='green', alpha=0.75, bins=range(0, 1000000000, 10000000))
      plt.loglog(bins[1:],hist,'r', marker='o')
      plt.xlabel('Dollar Trade')
      plt.ylabel('Probability')
      plt.title("Dollar Distribution"+str(year))
      plt.show()

    
  return 0

def trade_reciprocity(years,resource):
  corrmeans = []
  for year in years:
    G = getGraph(year,resource)
    corrcoeffs = []
    [xs,ys] = [[],[]]
    for country in G.nodes():
      for e in G.edges(country):
        try:
          [x1,y1] = [G[e[0]][e[1]],G[e[1]][e[0]]]
          #print [x1,y1]
          xs.append(x1['weight'])
          ys.append(y1['weight'])
        except KeyError:
          'whoops'
    if len(xs)>1:
      cc = np.corrcoef([xs,ys])
      corrcoeffs.append(cc[0][1])
    #print corrcoeffs
    corrmeans.append(np.mean(corrcoeffs))
    print [year,np.mean(corrcoeffs)]
  write({'means':corrmeans, 'years':years},'data/raw/comtrade/explore/'+resource[0],'/meanReciprocityCorrelation')
  plt.plot(years,corrmeans)
  plt.title('Mean Correlation of Import/Export By Year')
  directory = checkpath('data/raw/comtrade/explore/'+resource[0]+'/images/')
  plt.savefig(directory+'meanReciprocityCorrelation.png')
  #plt.show()
  return 0

if __name__ == '__main__':
  years = range(1962,2012)
  resources = {'total':['sitc-total', 'S1_TOTAL']}
  #resources = {'fuel':['fuelOil19882011', '27']}

  for r in resources:
    resource = resources[r]
    directory = checkpath('data/raw/comtrade/explore/'+resource[0])
    directory = checkpath('data/raw/comtrade/explore/'+resource[0]+'/images/')
    #print nodeset
    #write(linksAddedPerYear(years,resource),'data/raw/comtrade/explore/'+resource[0],'/links')
    #write(extractLinkRatios(years,resource),'data/raw/comtrade/explore/'+resource[0],'/ratios')
    #linkRatioStats('data/raw/comtrade/explore/'+resource[0]+'/ratios')
    #graphImage(years,r,resource)

    #trade_reciprocity(years,resource)
    #extractLinkRatios(years,resource)
    #p_newEdge_degree(years, resource)
    #graphImage(years,r,resource)
    macroEvolution(years, resource)
