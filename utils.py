import os
import pickle
import networkx as networkx
import matplotlib
import matplotlib.pyplot as plt
#Stupid git
def checkpath(folderPath):
  if not os.path.exists(folderPath):
    os.makedirs(folderPath)
  return folderPath

def write(D,directory,filename):
  checkpath(directory)
  f = open(directory+filename+'.txt', 'w')
  pickle.dump(D,f)
  f.close()
  return 1

def read(filename):
  f = open(filename+'.txt', 'r')
  data = pickle.load(f)
  f.close()
  return data

def prune_countries(G):
  naughtyCountries = read('data/raw/comtrade/metadata/naughtyCountryList')
  for c in naughtyCountries:
    G.remove_node(c)
  return G

def plot_distribution(X,Y,directory,title):
  checkpath(directory)
  fig = plt.figure()
  fig.clf()
  ax = fig.add_subplot(111)
  ax.plot(X,Y)
  ax.set_xscale('log')
  ax.set_yscale('log')
  plt.title(title)
  fig.savefig(directory+title+".png")

def degree_distribution(G):
  degs = {}
  for n in G.nodes():
    deg = G.degree(n)
    if deg not in degs:
      degs[deg] = 0
    degs[deg] += 1
  return sorted(degs.items())