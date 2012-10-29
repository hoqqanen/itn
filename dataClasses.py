class IndicatorData:
  def __init__(self, indicator, description, data, source=''):
    self.indicator = indicator
    self.description = description
    self.data = data #In the form [country:[year:value]]
    self.source = source