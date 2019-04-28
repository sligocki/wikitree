class DefaultList:
  """List which automatically extends itself to indexes accessed."""

  def __init__(self, default_func):
    self.data = []
    self.default_func = default_func

  def resize(self, index):
    while index >= len(self):
      self.data.append(self.default_func())

  def __getitem__(self, index):
    self.resize(index)
    return self.data[index]

  def __setitem__(self, index, value):
    self.resize(index)
    self.data[index] = value

  def __len__(self):
    return len(self.data)


def print_stats(dists):
  print "People connected:", "{:,}".format(len(dists))

  hist = DefaultList(int)
  total = 0
  for per in dists:
    hist[dists[per]] += 1
    total += dists[per]

  #print hist.data
  people_to_median = len(dists) // 2
  i = 0
  while hist[i] < people_to_median:
    people_to_median -= hist[i]
    i += 1
  median = i

  print "Mean distance:", float(total) / len(dists)
  print "Median distance:", median
  print "Max distance:", len(hist) - 1
