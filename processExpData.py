import csv
import networkx as nx
import csv
from utils import check_path, read, write, prune_countries, plot_distribution, degree_distribution


years=range(1950, 2001,1)
gs={}
for year in years:
  gs[year]=nx.DiGraph()

ifile  = open('/Users/ellerywulczyn/Desktop/CS224W/itn/data/raw/expdata.asc', "rb")
reader = csv.reader(ifile, delimiter=' ')

rownum = 0
for row in reader:
    # Save header row.
    if rownum == 0:
        header = row
    else:

      year=int(row[4])
      if year in years:
        #print row
        a=row[0]
        b=row[2]
        exp_a_b=float(row[5])
        exp_b_a=float(row[9])
        gdp_a=float(row[14])
        gdp_b=float(row[18])
        pop_a=float(row[13])
        pop_b=float(row[17])
        if( not a in gs[year].nodes()):
         gs[year].add_node(a, gdp=gdp_a, pop=pop_a)
        if( not b in gs[year].nodes()):
          gs[year].add_node(b, gdp=gdp_b, pop=pop_b)
        if exp_a_b>0:
          gs[year].add_edge(a, b, weight=exp_a_b)
        if exp_b_a>0:
          gs[year].add_edge(b, a, weight=exp_b_a)      
    rownum += 1
    print rownum

ifile.close()

for year in years:
  write(gs[year],'data/raw/essex/pickles/',str(year))
