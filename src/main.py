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
      center = ((points[0][0] + points[1][0])/2, (points[0][1] +
          points[1][1])/2)
      cv.Circle(img, center, 10, im.color.BLUE, 3)



def mainLoop():
  # Setting up the window objects and environment
  proc_win_name = "Processing window"
  cam_win_name = "Capture from camera"
  proc_win = cv.NamedWindow(proc_win_name, 1)
  cam_win = cv.NamedWindow(cam_win_name, 1)
  cam = cv.CaptureFromCAM(0)
  cv.SetMouseCallback(proc_win_name, handle_mouse)
  cv.SetMouseCallback(cam_win_name, handle_mouse)
  msdelay = 3
  initHueThreshold = 42
  initIntensityThreshold = 191
  skin_detector = skin.SkinDetector()
  motion_util = motion2.MotionUtility()
  cv.CreateTrackbar('l_hueThreshold',
                    proc_win_name,
                    SDC.GSD_HUE_LT,
                    255,
                    skin_detector.setHueThresholdLow)
  cv.CreateTrackbar('h_hueThreshold',
                    proc_win_name,
                    SDC.GSD_HUE_UT,
                    255,
                    skin_detector.setHueThresholdHigh)
  cv.CreateTrackbar('l_intensityThreshold',
                    proc_win_name,
                    SDC.GSD_INTENSITY_LT,
                    255,
                    skin_detector.setIntensityThresholdLow)
  cv.CreateTrackbar('h_intensityThreshold',
                    proc_win_name,
                    SDC.GSD_INTENSITY_UT,
                    255,
                    skin_detector.setIntensityThresholdHigh)

  session = ImageProcessSession(skin_detector, motion_util)
  while True:
    k = cv.WaitKey(msdelay)
    k = chr(k) if k > 0 else 0
    if handle_keyboard(k) < 0:
        break
    bgrimg = cv.QueryFrame(cam)
    if not bgrimg:
        break
    cv.Flip(bgrimg, None, 1)

    #session.process(bgrimg)
    contours = session.process(bgrimg)

    img = cv.CreateImage((bgrimg.width, bgrimg.height), 8, 3)

    if contours:
        max_contours = im.top_three_max_contours(contours)

    if max_contours:
        cts = []
        for ct in max_contours:
            if ct[1]: cts.append(ct[1])
        finger_tips = im.get_finger_tips(cts, img)

    session.translate(finger_tips, img)
    cv.ShowImage(proc_win_name, img)


if __name__=='__main__':
    try:
        mainLoop()
    except Exception, e:
        print "Unkown error: ", e 
