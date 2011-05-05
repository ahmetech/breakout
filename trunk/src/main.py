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
    
    session.process(bgrimg)
    contours = session.process(bgrimg)

    img = cv.CreateImage((bgrimg.width, bgrimg.height), 8, 3)
    if contours:
        x, y, r, b = im.find_max_rectangle(contours)
        # adjust ratio
        ratio = abs(float(y-b)/(x-r))
        if ratio > 2:
            b = y + abs(x-r)*2

        cv.Rectangle(img, (x,y), (r, b), im.color.RED)
        rotate_center = ((x+r)/2, y+100)
        # draw center
        cv.Circle(img, rotate_center, 5,
             (255, 0, 255, 0),
             cv.CV_FILLED, cv.CV_AA, 0)

        (area, max_contours) = im.max_area(contours)
        cv.DrawContours(img, max_contours, im.color.RED, im.color.GREEN, 1,
            thickness=3)
        # Draw the convex hull as a closed polyline in green
        hull = im.find_convex_hull(max_contours)
        if (hull != None):
            cv.PolyLine(img, [hull], 1, cv.RGB(0,255,0), 3, cv.CV_AA)
            tip = im.find_finger_tip(hull, img)
    cv.ShowImage(proc_win_name, img)


if __name__=='__main__':
    try:
        mainLoop()
    except (TypeError, cv.error), e:
        print "out error", e 
