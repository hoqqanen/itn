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
from random import sample

def PCA(years, resource, toCountries, typen):
  assert(len(toCountries)==1)
  gs={}
  cList=[]
  for y in years:
    gs[y]=get_graph(y, resource)
    cList.append(set(gs[y].nodes()))
  countries = list(set.intersection(*cList))
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

  cy=np.zeros((m, len(years)))
  for c in range(m):
    print countries[c]
    for y in range(len(years)):
      tt=sum([gs[years[y]][countries[c]][to]["weight"] for to in gs[years[y]][countries[c]]])
      if tt==0:
        tt=1
      cy[c, y]=tt

  if typen=="proportion":    
    for c in range(m):
      for y in range(len(years)):
        a[c,y]=(a[c,y]/float(cy[c,y]))*100
        print a[c,y]
  

  for j in range(n):
    avg=sum(a[:,j])/float(m)
    print "avg", avg
    a[:,j]=a[:,j]-avg
    var=np.dot(a[:,j], a[:,j])
    print "var", var
    a[:,j]=a[:,j]/var**0.5
    print np.dot(a[:,j], a[:,j])

  u,s,v=np.linalg.svd(a)
  plt.plot(s)
  plt.show()
  plt.scatter(u[:,0]*s[0], u[:,1]*s[1])
  plt.show()

  labels = countries
  plt.subplots_adjust(bottom = 0.1)
  plt.scatter(
    u[:,0]*s[0], u[:,1]*s[1], marker = 'o', c = u[:,0]*s[0], s = np.ones(len(u[:,1])),
    cmap = plt.get_cmap('Spectral'))
  for label, x, y in zip(labels, u[:,0]*s[0], u[:,1]*s[1]):
    plt.annotate(
        label, 
        xy = (x, y), xytext = (-20, 20),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

  plt.show()





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
  plt.savefig(get_images_directory(resource)+'p(new link to|d).png')
  plt.clf()
  plt.hist(fromCounts, normed=False,  bins=range(0, 200, 10))
  plt.title("p(new link from|d)")
  plt.savefig(get_images_directory(resource)+'p(new link from|d).png')



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
    densities.append(len(g.edges())/float(len(g.nodes())))
    diameters.append(SampledDiameter(g))
  plt.clf()
  plt.plot(years, densities)
  plt.title("Density Evolution")
  plt.savefig(get_images_directory(resource)+'density'+'.png')

  plt.clf()
  plt.plot(years, diameters)
  plt.title("Diameter Evolution")
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
    plt.savefig(get_images_directory(resource)+'degreeHist'+str(y)+'.png')
    plt.clf()


def linkRatioStats(filepath):
  yearlyRatios = read(filepath)
  means = []
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
      plt.loglog(bins[1:],hist,'r', marker='o')
      plt.xlabel('Ratio')
      plt.ylabel('Probability')
      plt.title("Ratio Distribution"+str(year))
      plt.savefig(get_images_directory(resource)+'RatioDistribution'+str(year)+'.png')

      plt.clf()
      ratioData=map(lambda x: x[4], filteredData)
      bins=range(0, 1000, 100)
      hist=np.histogram(ratioData, density=True, bins=bins)[0]
      #n, bins, patches = plt.hist(map(lambda x: x[4], filteredData), normed=1, facecolor='green', alpha=0.75, bins=range(0, 1000000000, 10000000))
      plt.loglog(bins[1:],hist,'r', marker='o')
      plt.xlabel('Dollar Trade')
      plt.ylabel('Probability')
      plt.title("Dollar Distribution"+str(year))
      plt.savefig(get_images_directory(resource)+'WeightDistribution'+str(year)+'.png')
    
  return 0

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
  directory = get_images_directory(resource)
  plt.savefig(directory+'meanReciprocityCorrelation.png')
  plt.clf()
  return 0

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
    #visualizeGraphs(years,resource)
    degreeDistributions(years, resource)
    trade_reciprocity(years,resource)
    p_newEdge_degree(years, resource)
    macroEvolution(years, resource)
    #PCA(years, resource, ["AFG"], "proportion")

