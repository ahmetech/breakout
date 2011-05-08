'''
    Gesture Combination Authentication Program.

    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import os
import sys
import cv
import im
import numpy
import skin, gesture
import motion2
import math
import traceback
import util
from constants import SDC


def handle_mouse(event, x, y, flags, param):
  pass

def handle_keyboard(key):
    ''' return 0 if normally handle the key else -1.'''
    if key == 'q':
      return -1
    elif key == 'c':
      print 'calibrate the skin detection parameters...'
      self.skin_detector.toggle_calibrate()
    return 0


class ImageProcessSession(object):
  """ ImageProcessSession is a high level filter manager object.
  """
  def __init__(self, skin_detector, motion_detector):
    self.skin_detector = skin_detector
    self.motion_detector = motion_detector
    self.history = []
    self.buf = []
    self.max_degree_change = 0.2
    self.max_pos_change = 50

    for i in range(5):
        self.history.append( ((-1, -1), 0.0) )

  def get_motion_mask(self, img):
      return self.motion_detector.get_motion_mask(img)
  
  def get_skin_mask(self, img):
      return self.skin_detector.detectSkin(img)

  def filter_by_motion(self, img):
      mask = self.get_motion_mask(img)
      cv.And(img, mask, img)
      return img

  def process(self, bgrimg):
    img = self.skin_detector.detectSkin(bgrimg)
    #cv.ShowImage("test2", img)
    #cv.Convert(img, bgrimg)
    motion_mask = self.get_motion_mask(bgrimg)
    #cv.ShowImage("motion", motion_mask)
    #cv.And(img, motion_mask, img)
    #cv.ShowImage("test3", img)
    contours = im.find_contours(img)
    return contours

  def translate(self, points, img):
      if len(points) < 2: return
      cv.Line(img, points[0], points[1], im.color.BLUE, 3) 
      polar = self.__calc_new_position(points)
      self.update_game(polar)
      cv.Circle(img, polar[0], 10, im.color.BLUE, 3)

  def __calc_new_position(self, points):
      p1, p2 = points[0], points[1]
      center = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
      theta = math.atan(float(p1[1] - p2[1])/(p2[0] - p1[0]))
      return (center, theta)

  def update_game(self, polar):
      last = self.history[-1]
      degree_change = abs(polar[1] - last[1]) 
      p1 = last[0]
      p2 = polar[0]
      pos_change = math.sqrt((p1[0] - p2[0])*(p1[0] - p2[0]) + (p1[1] -
          p2[1])*(p1[1] - p2[1]))
      print pos_change, degree_change
      if pos_change > self.max_pos_change or degree_change >\
          self.max_degree_change: 
              self.buf.append(polar)
              if len(self.buf) > 5: self.buf.pop(0)
              print "put to buf"
              if self.__check_buffer_stable():
                  print "ss"
                  self.history = self.buf
                  self.buf = []
              else: print "not ssssssssssssssssss"

      else:
          self.history.append(polar)
          self.history.pop(0)
          self.buf = []
          print "put into history"

  def __check_buffer_stable(self):
      stable = True
      if len(self.buf) < 5: return False
      for i in range(4):
          p1 = self.buf[i][0]
          p2 = self.buf[i+1][0]
          d1 = self.buf[i][1]
          d2 = self.buf[i+1][1]
          delta_p = util.get_point_distance(p1, p2)
          delta_d = abs(d1 - d2)
          if delta_p > self.max_pos_change or delta_d > self.max_degree_change:
              stable = False
      return True


class Entry(object):
  # Setting up the window objects and environment
  debug = 1 
  proc_win_name = "Processing window"
  cam_win_name = "Capture from camera"
  msdelay = 3

  def initWindows(self):
     cv.SetMouseCallback(self.proc_win_name, handle_mouse)
     cv.SetMouseCallback(self.cam_win_name, handle_mouse)
     proc_win = cv.NamedWindow(self.proc_win_name, 1)
     cam_win = cv.NamedWindow(self.cam_win_name, 1)

  def __init__(self):
     self.initWindows()
     self.cam = cv.CaptureFromCAM(0)
     skin_detector = skin.SkinDetector()
     motion_util = motion2.MotionUtility()
     cv.CreateTrackbar('l_hueThreshold',
                    self.proc_win_name,
                    SDC.GSD_HUE_LT,
                    255,
                    skin_detector.setHueThresholdLow)
     cv.CreateTrackbar('h_hueThreshold',
                    self.proc_win_name,
                    SDC.GSD_HUE_UT,
                    255,
                    skin_detector.setHueThresholdHigh)
     cv.CreateTrackbar('l_intensityThreshold',
                    self.proc_win_name,
                    SDC.GSD_INTENSITY_LT,
                    255,
                    skin_detector.setIntensityThresholdLow)
     cv.CreateTrackbar('h_intensityThreshold',
                    self.proc_win_name,
                    SDC.GSD_INTENSITY_UT,
                    255,
                    skin_detector.setIntensityThresholdHigh)
     self.session = ImageProcessSession(skin_detector, motion_util)

  def run(self):
    k = cv.WaitKey(self.msdelay)
    k = chr(k) if k > 0 else 0
    if handle_keyboard(k) < 0:
        return False
    bgrimg = cv.QueryFrame(self.cam)
    if not bgrimg:
        return False
    cv.Flip(bgrimg, None, 1)

    contours = self.session.process(bgrimg)

    img = cv.CreateImage((bgrimg.width, bgrimg.height), 8, 3)

    if contours:
        max_contours = im.top_two_max_contours(contours)

    if max_contours:
        cts = []
        for ct in max_contours:
            if ct[1]: cts.append(ct[1])
        finger_tips = im.get_finger_tips(cts, img)

    self.session.translate(finger_tips, img)
    if self.debug == 1: cv.ShowImage(self.proc_win_name, img)
    return True


def mainLoop():
    entry = Entry()
    while True:
       if not entry.run():
          break

if __name__=='__main__':
    try:
        mainLoop()
    except Exception, e:
        print "Unkown error: ", e 
        raise
