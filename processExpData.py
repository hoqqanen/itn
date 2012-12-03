import csv
import networkx as nx
import csv
from utils import check_path, read, write, prune_countries, plot_distribution, degree_distribution

CONVERTER = {
    'ATG' : 'AAB',
    'DZA' : 'ALG',
    'AGO' : 'ANG',
    'AUS' : 'AUL',
    'BHR' : 'BAH',
    'BRB' : 'BAR',
    'BFA' : 'BFO',
    'BHS' : 'BHM',
    'BTN' : 'BHU',
    'BGD' : 'BNG',
    'BIH' : 'BOS',
    'BWA' : 'BOT',
    'BRN' : 'BRU',
    'BDI' : 'BUI',
    'BGR' : 'BUL',
    'KHM' : 'CAM',
    'CMR' : 'CAO',
    'CPV' : 'CAP',
    'CIV' : 'CDI',
    'CAF' : 'CEN',
    'TCD' : 'CHA',
    'COG' : 'CON',
    'CRI' : 'COS',
    'HRV' : 'CRO',
    'CZE' : 'CZR',
    'DNK' : 'DEN',
    'COD' : 'DRC',
    'VNM' : 'DRV',
    'GNQ' : 'EQG',
    'FRA' : 'FRN',
    'GMB' : 'GAM',
    'DEU' : 'GFR',
    'GEO' : 'GRG',
    'GRD' : 'GRN',
    'GTM' : 'GUA',
    'GIN' : 'GUI',
    'HTI' : 'HAI',
    'HND' : 'HON',
    'ISL' : 'ICE',
    'IDN' : 'INS',
    'IRN' : 'IRE',
    'KIR' : 'KBI', # guessed
    'KWT' : 'KUW',
    'KGZ' : 'KYR',
    'KAZ' : 'KZK',
    'LVA' : 'LAT',
    'LBN' : 'LEB',
    'LSO' : 'LES',
    'LBR' : 'LIB',
    'LTU' : 'LIT',
    'MKD' : 'MAC',
    'MRT' : 'MAA',
    'MDV' : 'MAD',
    'MDG' : 'MAG',
    'MYS' : 'MAL',
    'MUS' : 'MAS',
    'MWI' : 'MAW',
    'MDA' : 'MLD',
    'MCO' : 'MNC',
    'MNG' : 'MON',
    'MAR' : 'MOR',
    'MHL' : 'MSI',
    'MMR' : 'MYA',
    'MOZ' : 'MZM',
    'NAM' : 'NAU',
    'NPL' : 'NEP',
    'NZL' : 'NEW',
    'NGA' : 'NIG',
    'NER' : 'NIR',
    'NLD' : 'NTH',
    'OMN' : 'OMA',
    'PLW' : 'PAL',
    'PRY' : 'PAR',
    'PHL' : 'PHI',
    'PRT' : 'POR',
    'KOR' : 'ROK',
    'ROU' : 'RUM', # not found
    'ZAF' : 'SAF',
    'SLV' : 'SAL',
    'SYC' : 'SEY',
    'SLE' : 'SIE',
    'SGP' : 'SIN',
    'KNA' : 'SKN',
    'SVK' : 'SLO',
    'LCA' : 'SLU',
    'SMR' : 'SNM',
    'SLB' : 'SOL',
    'ESP' : 'SPN',
    'LKA' : 'SRI',
    'SDN' : 'SUD', # also south sudan
    'VCT' : 'SVG',
    'SWZ' : 'SWA',
    'SWE' : 'SWD',
    'CHE' : 'TAJ',
    'TWN' : 'TAW',
    'TZA' : 'TAZ',
    'THA' : 'THI',
    'TGO' : 'TOG',
    'TTO' : 'TRI',
    'ARE' : 'UAE',
    'GBR' : 'UKG',
    'URY' : 'URU',
    'VUT' : 'VAN',
    'SRB' : 'YUG', # split into serbia and montenegro
    'ZMB' : 'ZAM',
    'ZWE' : 'ZIM',
    }
CONVERTER = {v: k for (k, v) in CONVERTER.items()}

years=range(1950, 2001,1)
gs={}
for year in years:
  gs[year]=nx.DiGraph()

ifile  = open('data/raw/exptradegdpv4.1/expdata.asc', "rb")
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
        a=CONVERTER.get(a, a)
        b=row[2]
        b=CONVERTER.get(b, b)

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
