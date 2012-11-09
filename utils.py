import os
import pickle
import networkx as networkx
import api.comtrade as ct
import matplotlib
import matplotlib.pyplot as plt

def get_graph(year,resource):
  try:
    G = read('data/raw/comtrade/data/'+resource[0]+'/pickles/'+str(year))
  except IOError:
    comtrade_country_xml = 'data/raw/comtrade/metadata/countries.xml'
    comtrade_file = 'data/raw/comtrade/data/'+resource[0]+'/'+resource[1]+'_'+str(year)+'.xml'
    G = ct.load_from_xml(comtrade_file, ct.read_country_data(comtrade_country_xml))
    write(G,'data/raw/comtrade/data/'+resource[0]+'/pickles/',str(year))
  G = prune_countries(G) #Remove the naughty list
  return G

def check_path(folderPath):
  if not os.path.exists(folderPath):
    os.makedirs(folderPath)
  return folderPath

def write(D,directory,filename):
  check_path(directory)
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
  check_path(directory)
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