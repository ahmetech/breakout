'''
    Image Utility
    
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import numpy
import cv
import matplotlib.pyplot as pyplot

class Color(object):
    pass

color=Color()
color.RED=(0,0,255,0)
color.GREEN=(0,255,0,0)
color.BLUE=(255,0,0,0)

class Font(object):
    pass

font = Font()
font.default = cv.InitFont(cv.CV_FONT_HERSHEY_DUPLEX, 1.0, 1.0, thickness=2)

def puttext(img, text, x, y):
  cv.PutText(img, text, (x,y), font.default, color.RED)

def cvimg2numpy(cvimg):
  return numpy.asarray(cv.GetMat(cvimg))
  
def bgr2hsv(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  hsvimg = cv.CreateImage(size, depth, channels)
  cv.CvtColor(cvimg, hsvimg, cv.CV_BGR2HSV)
  return hsvimg
  
def bgr2gray(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  grayimg = cv.CreateImage(size, depth, 1)
  cv.CvtColor(cvimg, grayimg, cv.CV_BGR2GRAY)
  return grayimg
  
def bgr2rgb(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  rgbimg = cv.CreateImage(size, depth, channels)
  cv.CvtColor(cvimg, rgbimg, cv.CV_BGR2RGB)
  return rgbimg

def rgb2bgr(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  bgrimg = cv.CreateImage(size, depth, channels)
  cv.CvtColor(cvimg, bgrimg, cv.CV_RGB2BGR)
  return bgrimg


def split3(cvimg):
  size = (cvimg.width, cvimg.height)
  c1 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
  c2 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)  
  c3 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
  cv.Split(cvimg, c1, c2, c3, None)
  return c1,c2,c3

def merge3(b,g,r):
  size = (r.width, r.height)
  img = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
  cv.Merge(b,g,r,None,img)
  return img
  
def size(cvimg):
  return (cvimg.width, cvimg.height)

def test_funcs():

  im = cv.LoadImage('me.jpg')
  im = bgr2hsv(im)
  h,s,v = split3(im)
  h = cvimg2numpy(h)
  s = cvimg2numpy(s)
  v = cvimg2numpy(v)
  
  print h.shape

  pyplot.figure(1)
  pyplot.imshow(h, cmap=pyplot.cm.gray)
  
  pyplot.figure(2)
  pyplot.imshow(s, cmap=pyplot.cm.gray)
  
  pyplot.figure(3)
  pyplot.imshow(v, cmap=pyplot.cm.gray)
  
  pyplot.figure(4)
  (n, bins) = numpy.histogram(h.flatten(), bins=30)
  binc = .5*(bins[1:]+bins[:-1])
  print binc[n.argmax()]


def find_contours(im):
    """ @param im IplImage: an input gray image
        @return cvseq contours using cv.FindContours
    """
    storage = cv.CreateMemStorage(0)
    try:
      contours = cv.FindContours(im, 
                               storage,
                               cv.CV_RETR_EXTERNAL,
                               cv.CV_CHAIN_APPROX_SIMPLE)
      contours = cv.ApproxPoly(contours,
                             storage,
                             cv.CV_POLY_APPROX_DP, 3, 1)
    except cv.error, e:
      print e
      return None
    return contours

def find_convex_hull(cvseq):
    """ @param cvseq cvseq: an input cvseq from cv.FindContours
        @return cvseq hull: convex hull from ConvexHull2
    """
    storage = cv.CreateMemStorage(0)
    try:
      hull = cv.ConvexHull2(cvseq, storage, cv.CV_CLOCKWISE, 0)
    except TypeError, e:
      return None
    return hull

def find_convex_defects(contour, hull):
    storage = cv.CreateMemStorage(0)
    return cv.ConvexityDefects(contour, hull, storage)


def max_area(contours):
    ''' returns the contour with maximal area. 
        @return: (max_area, max_contour)
    '''
    max_area = 0
    max_contours = contours
    try:
      while True:
          area = cv.ContourArea(contours)
          if area > max_area:
              max_area = area
              max_contours = contours
          contours = contours.h_next()
    except (TypeError, cv.error), e:
      return max_area, max_contours
    return max_area, max_contours

def find_max_rectangle(contours):
    max_a, contours = max_area(contours)
    left, top, w, h = cv.BoundingRect(contours)
    right = left + w
    bottom = top + h
    return left, top, right, bottom

def plot_contours(contours, shape):
    img = cv.CreateImage(shape, 8, 3)
    cv.NamedWindow('show', 1)
    cv.SetZero(img)
    cv.DrawContours(img, contours, color.RED, color.GREEN, 1)
    cv.ShowImage('show', img)


if __name__=='__main__':
  im = cv.LoadImage('orig.png')
  #im = bgr2gray(im)
  b,g,r = split3(im)
  im2 = merge3(b,g,r)
  cv.SaveImage('out.png', im2)
  exit(0)
  contours = find_contours(im)
  area = cv.ContourArea(contours)
  print area
  hull = find_convex_hull(contours)
  defects = find_convex_defects(contours, hull)
  print defects
  plot_contours(contours, (im.width, im.height))
  raw_input()
