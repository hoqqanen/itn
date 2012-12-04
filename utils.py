import os
import pickle
<<<<<<< HEAD
=======
import networkx as nx
import api.comtrade as ct
>>>>>>> b3751db9ac4540034818b8a4554c31658d7f7152
import matplotlib
import matplotlib.pyplot as plt
import networkx as networkx

<<<<<<< HEAD
import api.comtrade as ct

def get_graph(year, resource):
=======
def get_graph(year, resource, subgraph = []):
>>>>>>> b3751db9ac4540034818b8a4554c31658d7f7152
  if resource=="essex":
    return read("data/raw/essex/pickles/"+str(year))
  else:
    try:
      G = read('data/raw/comtrade/data/'+resource[0]+'/pickles/'+str(year))
    except IOError:
      comtrade_country_xml = 'data/raw/comtrade/metadata/countries.xml'
      comtrade_file = 'data/raw/comtrade/data/'+resource[0]+'/'+resource[1]+'_'+str(year)+'.xml'
      G = ct.load_from_xml(comtrade_file, ct.read_country_data(comtrade_country_xml))
      write(G,'data/raw/comtrade/data/'+resource[0]+'/pickles/',str(year))
    #G = prune_countries(G) #Remove the naughty list
    #G = get_subgraph(G, subgraph)
    eu = ['USA','Austria','Belgium','Bulgaria','Cyprus','Czech Republic','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden','United Kingdom']
    #G = get_subgraph(G, eu)
    qq = read('data/raw/countryCodes')
    G2 = nx.relabel_nodes(G,qq)
    G3 = read("data/raw/essex/pickles/"+str(year))
    for n in list(set(G2.nodes()).intersection(set(G3.nodes()))):
      G2.node[n]['gdp'] = G3.node[n]['gdp']
      G2.node[n]['pop'] = G3.node[n]['pop']
      print [n,G2.node[n]['gdp']]
    for e in G2.edges(data=True):
      G2[e[0]][e[1]]['weight'] = float(G2[e[0]][e[1]]['weight'])
    return G2

def convert_country_code(D,converter):
  if type(D)==type({}):
    newD = {}
    for k in D:
      newD[converter[k]] = D[k]
  else:
    newD = converter[D]
  return newD

def ct_to_wb(name,ctCode,wbName):
  return wbName[ctCode[name]]
  

def get_images_directory(resource):
  if(resource=="essex"):
    return 'data/raw/essex/images/'
  else:
    return 'data/raw/comtrade/explore/'+resource[0]+'/images/'

def get_results_directory(resource):
  if(resource=="essex"):
    return 'data/raw/essex/'
  else:
    return 'data/raw/comtrade/explore/'+resource[0]+'/'

#Stupid git
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
  #G["India"]=G["India, excl. Sikkim"]
  naughtyCountries.extend(["US Misc. Pacific Isds", "Other Asia, nes",\
   "Fmr Rhodesia Nyas", "United States Minor Outlying Islands", "Fmr Tanganyika",\
    "Bunkers", "South Georgia and the South Sandwich Islands", "Br. Indian Ocean Terr.", \
    "Fmr Panama, excl.Canal Zone", "India, excl. Sikkim", "So. African Customs Union"\
    "Saint Kitts, Nevis and Anguilla", "China, Macao SAR","Antarctica"  \
    ])
  for c in naughtyCountries:
    try:
      G.remove_node(c)
      print "removed node: ", c
    except:
      pass
  return G

def get_subgraph(G,s):
  for c in G.nodes():
    if c not in s:
      G.remove_node(c)
      #print "removed node: ", c
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
  plt.show()
  fig.savefig(directory+title+".pdf")

def degree_distribution(G):
  degs = {}
  for n in G.nodes():
    deg = G.degree(n)
    if deg not in degs:
      degs[deg] = 0
    degs[deg] += 1
  return sorted(degs.items())
