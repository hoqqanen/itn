"""Unused / deprecated"""

import csv


class worldEconomicOutlook():
	
	def __init__(self):
		ifile  = open('../WEOOct2012all.csv', "rb")
		self.reader = csv.reader(ifile)
		self.countries={}
		self.getCountries()
		self.indicators={}
		self.getIndicators()
		print self.countries.keys()
		print len(	self.countries)
		print self.indicators.keys()
		ifile.close()
		
	def getCountries(self):
		for row in self.reader:
			self.countries[row[3]]=""
        		
					
	def getIndicators(self):
		for row in self.reader:
			print row[4]
			self.indicators[row[4]]=""


if __name__ == "__main__":
	o=worldEconomicOutlook()
