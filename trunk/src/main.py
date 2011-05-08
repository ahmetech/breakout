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
      sys.exit(0)
    elif key == 'c':
      print 'calibrate the skin detection parameters...'
      self.skin_detector.toggle_calibrate()
    return 0


class ImageProcessSession(object):
  """ ImageProcessSession is a high level filter manager object.
  """
  def __init__(self, skin_detector, motion_detector, entry):
    self.skin_detector = skin_detector
    self.motion_detector = motion_detector
    self.entry = entry
    self.history = []
    self.buf = []
    self.max_degree_change = 0.2
    self.min_degree_change = 0.02
    self.max_pos_change = 50
    self.min_pos_change = 5
    self.history_size = 10
    self.win_w = 0
    self.win_h = 0
    for i in range(self.history_size):
        self.history.append( ((-1, -1), 0.0) )

  def set_size(self, img):
      self.win_w = img.width
      self.win_h = img.height

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
    #motion_mask = self.get_motion_mask(bgrimg)
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
      if p2[0] - p1[0] == 0: 
          theta = math.pi / 2
      else:
          theta = math.atan(float(p1[1] - p2[1])/(p2[0] - p1[0]))
      return (center, theta)

  def update_game(self, polar):
      last = self.history[-1]
      degree_change = abs(polar[1] - last[1]) 
      p1 = last[0]
      p2 = polar[0]
      pos_change = util.get_point_distance(p1, p2)
      print pos_change, degree_change
      if pos_change > self.max_pos_change or degree_change >\
          self.max_degree_change: 
              self.buf.append(polar)
              if len(self.buf) > self.history_size: self.buf.pop(0)
              if self.__check_buffer_stable():
                  print "buf is determined to be stabe, replace history with buf"
                  self.history = self.buf
                  self.buf = []
              else:
                  print "buf is not stable, this move is abandoned."
                  return

      else:
          self.history.append(polar)
          self.history.pop(0)
          self.buf = []

      current = self.history[-1]
      last = self.history[-2]
      right = current[0][0] - last[0][0]
      down = current[0][1] - last[0][1]
      d = math.sqrt(right*right + down*down)
      theta = current[1]
      print right, down, theta
      if d > self.min_pos_change:
          self.entry.move(right*2, down*2)
      else:
          print "ignore small movement"
          #self.__check_on_edge(current)
      self.entry.setAngle(theta/math.pi*180)
  
  def __check_on_edge(self, p):
      right = 0
      down = 0
      print self.win_w, self.win_h
      if p[0] < 10:
          right = -10
      if p[0] > self.win_w - 10:
          right = 10
      if p[1] < 10:
          down = -10
      if p[1] > self.win_h - 10:
          down = 10
      if right != 0 or down != 0:
          self.entry.move(right, down)

  def __check_buffer_stable(self):
      stable = True
      if len(self.buf) < self.history_size: return False
      for i in range(self.history_size - 1):
          p1 = self.buf[i][0]
          p2 = self.buf[i+1][0]
          d1 = self.buf[i][1]
          d2 = self.buf[i+1][1]
          delta_p = util.get_point_distance(p1, p2)
          delta_d = abs(d1 - d2)
          if delta_p > self.max_pos_change or delta_d > self.max_degree_change:
              stable = False
      return stable


class Entry(object):
  # Setting up the window objects and environment
  debug = 1 
  proc_win_name = "Processing window"
  msdelay = 3

  def initWindows(self):
     cv.SetMouseCallback(self.proc_win_name, handle_mouse)
     proc_win = cv.NamedWindow(self.proc_win_name, 1)

  def setCallbacks(self, moveCallback, setAngleCallback):
     self.move = moveCallback
     self.setAngle = setAngleCallback

  def __init__(self):
     self.move = None
     self.setAngle = None
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
     self.session = ImageProcessSession(skin_detector, motion_util, self)
     img = cv.QueryFrame(self.cam)
     img = im.resize(img, width=400)
     self.session.set_size(img)

  def run(self):
    k = cv.WaitKey(self.msdelay)
    k = chr(k) if k > 0 else 0
    if handle_keyboard(k) < 0:
        return False
    bgrimg = cv.QueryFrame(self.cam)
    if not bgrimg:
        return False
    bgrimg = im.resize(bgrimg, width=400)
    cv.Flip(bgrimg, None, 1)

    contours = self.session.process(bgrimg)

    max_contours = None
    if contours:
        max_contours = im.top_two_max_contours(contours)

    if max_contours:
        img = bgrimg
        #cv.Clone(bgrimg)
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
