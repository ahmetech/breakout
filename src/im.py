'''
    Image Utility
    
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import numpy
import cv
import math
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

def newgray(cvimg_or_size):
  size = None
  if isinstance(cvimg_or_size, (tuple, list)):
    size = tuple(cvimg_or_size)
  else:
    size = (cvimg_or_size.width, cvimg_or_size.height)
  return cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)


def size(cvimg):
  return (cvimg.width, cvimg.height)

def resize(src, width=None, height=None):
  assert width or height
  if not width:
     width = int(height * float(src.width)/float(src.height))
  if not height:
     height = int(width * float(src.height)/float(src.width))
  
  img = cv.CreateImage((width, height), src.depth, src.nChannels)
  cv.Resize(src, img)
  return img

def clone(src, _type='gray2bgr'):
    """
        Clone the image.
        @param _type: a string, and it can be one of the following:
            "gray2bgr"
        @returns: the cloned image
    """
    if _type.lower() == "gray2bgr":
        ret = cv.CreateImage((src.width, src.height), cv.IPL_DEPTH_8U, 3)
        r = cv.CloneImage(src)
        g = cv.CloneImage(src)
        b = cv.CloneImage(src)
        cv.Merge(r,g,b,None,ret)
        return ret
    else:
        raise ValueError("Unknown _type value.")


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

def vertices(contour):
  vt = set([])
  try:
      while True:
          vt = vt.union(set(list(contour)))
          contour = contour.h_next()
  except (TypeError, cv.error), e:
      return list(vt)
  return list(vt)


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
      #contours = cv.ApproxPoly(contours,
      #                       storage,
      #                       cv.CV_POLY_APPROX_DP, 3, 1)
    except cv.error, e:
      return None
    return contours

def find_convex_hull(cvseq):
    """ @param cvseq cvseq: an input cvseq from cv.FindContours
        @return cvseq hull: convex hull from ConvexHull2
    """
    storage = cv.CreateMemStorage(0)
    try:
      hull = cv.ConvexHull2(cvseq, storage, cv.CV_CLOCKWISE, 1)
    except TypeError, e:
      print "Find convex hull failed"
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

def top_three_max_contours(contours):
    max_contours = [(0, None), (0, None), (0, None)]

    try:
      while True:
          area = cv.ContourArea(contours)
          if area > max_contours[0][0]:
              max_contours[0] = (area, contours)
              max_contours.sort(cmp_contours)
          contours = contours.h_next()
    except (TypeError, cv.error), e:
      return max_contours
    return max_contours

def cmp_contours(c1, c2):
    if (c1[0] == c2[0]): 
        return 0
    elif (c1[0] > c2[0]): 
        return 1
    else:
        return -1

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

def find_finger_tip(hull,img):
    min_y = 1000
    min_p = (-1, -1) 

    if len(hull) < 4: return min_p

    for i in range(len(hull)):
        p = hull[i]
        if p[1] >= min_y: continue
        # calculate the angle between the 3 points
        a = b = c = 0
        l = r = i
        lp = rp = p
        min_distance = 20
        while (a < min_distance):
            l = (l-1)%len(hull)
            if l == i: break # finished one round and not find a suitable point
            lp = hull[l]  # left sibling with enough distance
            a = math.sqrt(pow(p[0] - lp[0], 2) + pow(p[1] - lp[1], 2))
        while (b < min_distance):
            r = (r+1)%len(hull)
            if r == i: break # finished one round and not find a suitable point
            rp = hull[r]  # right sibling with enough distance
            b = math.sqrt(pow(p[0] - rp[0], 2) + pow(p[1] - rp[1], 2))
        c = math.sqrt(pow(lp[0] - rp[0], 2) + pow(lp[1] - rp[1], 2))
        theta = math.acos(float(a*a + b*b - c*c)/(2*a*b))
        if theta*3 > math.pi: continue # > 60 degree
        min_y = p[1]
        min_p = p
    cv.Circle(img, min_p, 5,
            (255, 0, 255, 0),
            cv.CV_FILLED, cv.CV_AA, 0)
    return min_p

def get_finger_tips(contours, img):
    finger_tips = []
    for ct in contours: 
        if not ct: break

        x, y, r, b = find_max_rectangle(ct)
        # adjust ratio to at least 1/2
        ratio = abs(float(y-b)/(x-r))
        if ratio > 2:
            b = y + abs(x-r)*2
        cv.Rectangle(img, (x,y), (r, b), color.RED)
        # draw center
        rotate_center = ((x+r)/2, y+100)
        cv.Circle(img, rotate_center, 5,
             (255, 0, 255, 0),
             cv.CV_FILLED, cv.CV_AA, 0)

        cv.DrawContours(img, ct, color.RED, color.GREEN, 1,
            thickness=3)
        # Draw the convex hull as a closed polyline in green
        hull = find_convex_hull(ct)
        if (hull != None):
            cv.PolyLine(img, [hull], 1, cv.RGB(0,255,0), 3, cv.CV_AA)
            tip = find_finger_tip(hull, img)
            if tip != (-1, -1): 
                finger_tips.append(tip)
    return finger_tips

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
