import api.comtrade as ct
import networkx as nx
import os
import pickle
import matplotlib
import matplotlib.pyplot as plt
from utils import get_graph, check_path, read, write, prune_countries, plot_distribution, degree_distribution, get_images_directory, get_results_directory
import numpy as np
import csv
#import scipy
import numpy as np
import matplotlib.pyplot as plt
#from random import 
import math

from featureExtract import f_distance_pairs
from plfit import plfit
from scipy import stats
#from featureExtract import getFeatureMatrix
#from plfit import plfit




def getTradeMatrix(years, resource, toCountries, datatype):
  gs={}
  cList=[]
  for y in years:
    gs[y]=get_graph(y, resource)
    cList.append(set(gs[y].nodes()))
  countries = list(set.intersection(*cList))
  print countries
  if toCountries==None:
    toCountries=countries

  print "num countries afer intersection", len(countries)
    
  n=len(years)*len(toCountries)
  m=len(countries)
  a=np.ones((m,n))
  

  for k in range(len(countries)):
    for i in range(len(years)):
      for j in range(len(toCountries)):
        try:
          a[k, (i+1)*(j+1)-1]=gs[years[i]][countries[k]][toCountries[j]]["weight"]
        except:
          pass
  if datatype=="raw":
    np.savetxt("raw.csv", a, delimiter=",")

  cy=np.zeros((m, len(years)))
  for c in range(m):
    print countries[c]
    for y in range(len(years)):
      tt=sum([gs[years[y]][countries[c]][to]["weight"] for to in gs[years[y]][countries[c]]])
      if tt==0:
        tt=1
      cy[c, y]=tt

  if datatype=="proportion":    
    for c in range(m):
      for y in range(len(years)):
        a[c,y]=(a[c,y]/float(cy[c,y]))*100
        print a[c,y]





def linksAddedPerYear(years,resource):
  #predicates = list of pairs of lambda expressions returning true/false
  predicates = [[lambda x: x[2]['weight']>0, lambda x: x[2]['weight']>0],[lambda x: x[2]['weight']>100000, lambda x: x[2]['weight']>200000]]
  links = {}
  for y in years[0:-2]:
    [G1,G2] = [get_graph(y,resource),get_graph(y+1,resource)]
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
    [G1,G2] = [get_graph(y,resource),get_graph(y+1,resource)]
    [E1,E2] = [G1.edges(data=True),G2.edges(data=True)]
    [newE1, newE2] = [filter(p[0],E1),filter(p[1],E2)]
    newE1simple = map(lambda x: (x[0],x[1]), newE1)
    addedEdges = filter(lambda x: (x[0],x[1]) not in newE1simple, newE2)
    print len(addedEdges)
    for e in addedEdges:
      toCounts.append(len(G2[e[1]]))
      fromCounts.append(len(G2[e[0]]))

  plt.clf()
  plt.hist(toCounts, normed=False, bins=range(0, 200, 10))
  plt.title("p(new link to|d)")
  plt.savefig(get_images_directory(resource)+'p(d| new link to).png')
  plt.clf()
  plt.hist(fromCounts, normed=False,  bins=range(0, 200, 10))
  plt.title("p(new link from|d)")
  plt.savefig(get_images_directory(resource)+'p(d| new link from).png')



def SampledDiameter(g):
  ns=g.nodes()
  pathLengths=[]
  for n in ns:
    paths=nx.single_source_shortest_path(g, n)
    pathLengths.extend([len(paths[n]) for n in paths.keys()])
  return max(pathLengths)

def macroEvolution(years, resource):
  densities=[]
  diameters=[]
  for y in years:
    g=get_graph(y,resource)
    numNodes=float(len(g.nodes()))
    numEdges=len(g.edges())
    densities.append(numEdges/(numNodes*(numNodes-1)))
    diameters.append(SampledDiameter(g))
  plt.clf()
  plt.plot(years, densities)
  plt.title("Density Evolution")
  plt.xlabel('Year')
  plt.ylabel('Density')
  plt.savefig(get_images_directory(resource)+'density'+'.png')

  plt.clf()
  plt.plot(years, diameters)
  plt.title("Diameter Evolution")
  plt.xlabel('Year')
  plt.ylabel('Diameter')
  plt.savefig(get_images_directory(resource)+'diameter'+'.png')



#Remains to be done: compute consecutive year ratios on each link
#Determine how to prune the graph//select a subset that is more meaningful
#   or do we not mind having many nodes of degree 0?
def extractLinkRatios(years,resource):
  ratios = {}
  for y in years[0:-1]:
    ratios[y] = []
    [G1,G2] = [get_graph(y,resource),get_graph(y+1,resource)]
    for e in G1.edges(data=True): #e is current year edge
      try:
        pastEdgeData = G2[e[0]][e[1]] #If it doesn't exist we except
        ratios[y].append((e[0],e[1],float(e[2]['weight'])/pastEdgeData['weight'],float(e[2]['weight']),pastEdgeData['weight']))
      except KeyError:
        bloop = 'bloop'
  return ratios

def visualizeGraphs(years,resource):
  for year in years:
    G = get_graph(year,resource)
    plt.clf()
  #Visualize the network
    ecolors = map(lambda e: e[2]['weight'], G.edges(data=True))
    pos=nx.spring_layout(G)
    nx.draw(G,pos=pos,node_size=80,with_labels=True)
    plt.savefig(get_images_directory(resource)+"graph"+str(year)+'.png')
  return 0

def degreeDistributions(years, resource):
  for y in years:
    g=get_graph(y, resource) 
    degrees=[]
    for n in g.nodes():
      degrees.append(len(g[n]))
    plt.clf()
    plt.hist(degrees)
    plt.xlabel('Degree')
    plt.ylabel('Counts')
    plt.title("Degree Distribution "+str(year))
    plt.savefig(get_images_directory(resource)+'degreeHist'+str(y)+'.png')
    plt.clf()

from math import log
def linkRatioStats(filepath):
  yearlyRatios = read(filepath)
  means = []
  alphas=[]
  for year in yearlyRatios:
    print year
    if int(year)>=1950:
      filteredData = filter(lambda x: x[3]>100 and x[4]>100, yearlyRatios[year])
      # the histogram of trade
      plt.clf()
      ratioData=map(lambda x: x[2], filteredData)
      bins=np.arange(0, 3, 0.01)
      hist=np.histogram(ratioData, density=True, bins=bins)[0]
      #n, bins, patches = plt.hist(ratioData, normed=1, facecolor='green', alpha=0.75, bins=np.arange(0, 3, 0.01))
      plt.scatter(map(lambda x: log(x),bins[1:]),map(lambda x: log(x),hist),'r', marker='o')
      plt.xlabel('Export Ratio exp(t)/exp(t+1)')
      plt.ylabel('Probability')
      plt.title("Export Ratio Distribution"+str(year))
      plt.savefig(get_images_directory(resource)+'RatioDistribution'+str(year)+'.png')

      plt.clf()
      ratioData=map(lambda x: x[4], filteredData)
      xmin=min(ratioData)
      ahat=1+len(ratioData)*(1/sum([math.log(s/xmin) for s in ratioData]))
      print "MLE ", ahat
      alphas.append(ahat)
      #print plfit(ratioData)
      bins=range(0, 1000, 100)
      hist=np.histogram(ratioData, density=True, bins=bins)[0]
      #n, bins, patches = plt.hist(map(lambda x: x[4], filteredData), normed=1, facecolor='green', alpha=0.75, bins=range(0, 1000000000, 10000000))
      plt.loglog(bins[1:],hist,'r', marker='o')
      plt.xlabel('Export')
      plt.ylabel('Probability')
      plt.title("Dollar Distribution"+str(year)+"  a="+str(ahat))
      plt.savefig(get_images_directory(resource)+'WeightDistribution'+str(year)+'.png')
  plt.clf()
  plt.plot(yearlyRatios.keys(), alphas)
  plt.xlabel('years')
  plt.ylabel('alphas')
  plt.title("Alphas")
  plt.savefig(get_images_directory(resource)+'WeightDistributionAlphas.png')
    
  return 0

def dist_cor(years, resource):
  cors=[]
  for year in years:
    G = get_graph(year,resource)
    distDict=f_distance_pairs(G, G.nodes(), year)
    E=G.edges(data=True)
    ws=[]
    ds=[]
    for e in E:
      ws.append(e[2]["weight"])
      ds.append(distDict[(e[0], e[1])])
    cors.append(stats.pearsonr(ws, ds)[0])
  plt.clf()
  print len(years)
  print len(cors)
  print years
  print cors
  plt.plot(years, cors)
  plt.title("Correlation of Distance and Trade Volume")
  plt.xlabel("year")
  plt.ylabel("correlation")
  plt.show()




def trade_reciprocity(years,resource):
  corrmeans = []
  for year in years:
    G = get_graph(year,resource)
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
  write({'means':corrmeans, 'years':years},get_results_directory(resource),'meanReciprocityCorrelation')
  plt.clf()
  plt.plot(years,corrmeans)
  plt.title('Mean Correlation of Import/Export By Year')
  plt.xlabel('Year')
  plt.ylabel('Mean Correlation of Import/Export')
  directory = get_images_directory(resource)
  plt.savefig(directory+'meanReciprocityCorrelation.png')
  plt.clf()
  return 0

def summary_stats(years,resource):
  assortativities = []
  clusterings = []
  densities = []
  wwassort = []
  for year in years:
    G = get_graph(year,resource)
    for country in G.nodes():
      ww = sum(map(lambda x: x[2]['weight'], G.edges(country,data=True)))
      G.node[country]['ww'] = ww
    #assortativities.append(nx.degree_assortativity_coefficient(G))
    #clusterings.append(nx.average_clustering(G.to_undirected()))
    #densities.append(len(G.edges())/(len(G.nodes())*len(G.nodes())+0.0))
    wwassort.append(nx.attribute_assortativity_coefficient(G,'ww'))
    #print [year, ]
  plt.clf()
  plt.plot(years,wwassort)
  plt.title('Assortativity by Node Weight')
  plt.xlabel('Year')
  plt.ylabel('Assortativity by Weight')
  directory = get_images_directory(resource)
  plt.savefig(directory+'assortweight.png')
  return 0

import operator
if __name__ == '__main__':
  years = range(1950,2001)
  #resources = {'total':['sitc-total', 'S1_TOTAL']}
  #resources = {'fuel':['fuelOil19882011', '27']}
  resources={"essex":"essex"}

  for r in resources:
    resource = resources[r]
    directory = check_path(get_results_directory(resource))
    directory = check_path(get_images_directory(resource))
    #print nodeset
    #write(linksAddedPerYear(years,resource),get_results_directory(resource),'links')
    #write(extractLinkRatios(years,resource),get_results_directory(resource),'ratios')
    #linkRatioStats(get_results_directory(resource)+'ratios')
    #degreeDistributions(years, resource)
    #trade_reciprocity(years,resource)
    #p_newEdge_degree(years, resource)
    #macroEvolution(years, resource)
    #visualizeGraphs(years,resource)
    dist_cor(years, resource)
    #summary_stats(years,resource)
    clist = ['USA','GFR','JPN','UKG','CAN','FRN', 'ITA']
    clist2 = {'USA':'b', 'GFR':'r', 'JPN':'g', 'UKG':'m', 'CAN':'k', 'FRN':'c', 'ITA':'y'}
    cd = {}
    for c in clist:
      cd[c] = []
    for y in years:
      G = get_graph(y,r)
      qq = sorted(nx.pagerank(G).iteritems(),key=operator.itemgetter(1), reverse=True)
      qqq = nx.pagerank(G) 
      for c in clist:
        cd[c].append(qqq[c])
      print [y,qq[0:6]]
    plt.clf()
    for c in clist:
      plt.plot(years,cd[c],clist2[c],label=c)
    plt.title('Pagerank of top Countries')
    plt.legend( ('USA','GFR','JPN','UKG','CAN','FRN', 'ITA'),loc='upper left')
    plt.xlabel('Year')
    plt.ylabel('Pagerank')
    #plt.show()
    directory = get_images_directory(r)
    plt.savefig(directory+'pagerank.png')
    """
    linkRatioStats(get_results_directory(resource)+'ratios')
    
    degreeDistributions(years, resource)
    trade_reciprocity(years,resource)
    p_newEdge_degree(years, resource)
    macroEvolution(years, resource)
    visualizeGraphs(years,resource)
    """
    #PCA(years, resource, ["AFG"], "proportion")
    #a, labels=getFeatureMatrix(1999)
    #getTradeMatrix(years, resource, None, "raw" )
