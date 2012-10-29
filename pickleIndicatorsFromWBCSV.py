import csv
import cPickle
from dataClasses import IndicatorData
from pprint import pprint
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--csvFile", dest="filename",
                  help="name of world bank database csv file")

parser.add_option("-d", "--destinationFolder", dest="destinationFolder",
                  help="name of the folder in which to place the pickle")



(options, args) = parser.parse_args()


file = options.filename
indicators={}

years=range(1960, 2012)
indices=range(4, 56)
yearIndices={}
for i in range(len(years)):
    yearIndices[years[i]]=indices[i]

reader = csv.reader(open(file),delimiter=',')
for row in reader:
    indicator=row[2]
    if indicator in indicators:
        for year in years:
            value=row[yearIndices[year]]
            if value=='':
                value=None
            else:
                value=float(value)
                
            indicators[indicator][year][row[0]]=value
    if indicator not in indicators and indicator!='Indicator Name':
        indicators[indicator]={}
        for year in years:
            indicators[indicator][year]={}
        for year in years: 
            value=row[yearIndices[year]]
            if value=='':
                value=None
            else:
                value=float(value)
                
            indicators[indicator][year][row[0]]=value


for indicator in indicators.keys():
    FILE = open(options.destinationFolder+"/"+indicator+".txt", 'w')
    cPickle.dump(indicators[indicator], FILE)
    FILE.close()
