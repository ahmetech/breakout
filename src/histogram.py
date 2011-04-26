'''
    Gesture Combination Authentication Program histogram submodule
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''


class Histogram(object):
  def __init__(self):
    self.bInit = False
    self.hist = None
    self.n, self.bins = None, None
    
  def show(self):
    binc = .5*(self.bins[1:]+self.bins[:-1])
    maxn = max(self.n)
    if maxn > self.threshold:
      print maxn, binc[self.n.argmax()]
      
  def calHist(self, himg):
    self.threshold = self.threshold_ratio * himg.width * himg.height
    himg = im.cvimg2numpy(himg)
    (self.n, self.bins) = numpy.histogram(himg, 
                              bins=30, 
                              range=(self.lower_bound,self.upper_bound))
    self.bInit = True

  def peak(self):
    binc = .5*(self.bins[1:]+self.bins[:-1])
    maxn = max(self.n)
    if maxn > self.threshold:
      return binc[self.n.argmax()]
    return None

  def mergeWith(self, himg, factor):
    print 'hist merging'
    pass

  def findCurveThresholds(self):
    pass


class HueHistogram(Histogram):
  threshold_ratio = 0.01
  @property
  def lower_bound(self):
    return SDC.GSD_HUE_LT
  @property
  def upper_bound(self):
    return SDC.GSD_HUE_UT

class IntensityHistogram(Histogram):
  threshold_ratio = 0.01
  @property
  def lower_bound(self):
    return SDC.GSD_INTENSITY_LT
  @property
  def upper_bound(self):
    return SDC.GSD_INTENSITY_UT
