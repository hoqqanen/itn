import os
import pickle
import networkx as networkx
import matplotlib
import matplotlib.pyplot as plt

def checkpath(folderPath):
  if not os.path.exists(folderPath):
    os.makedirs(folderPath)

def write(D,directory,filename):
  checkpath(directory)
  f = open(directory+filename+'.txt', 'w')
  pickle.dump(D,f)
  f.close()
  return 1

def plot_distribution(X,Y,directory,title):
  checkpath(directory)
  fig = plt.figure()
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