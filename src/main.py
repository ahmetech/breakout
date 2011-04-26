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
  def __init__(self, skin_detector):
    self.skin_detector = skin_detector

  def process(self, bgrimg):
    img = self.skin_detector.detectSkin(bgrimg)
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
  #skin_detector.setHueThreshold(initHueThreshold)
  #skin_detector.setIntensityThreshold(initIntensityThreshold)
  cv.CreateTrackbar('l_hueThreshold',
                    proc_win_name,
                    initHueThreshold,
                    255,
                    skin_detector.setHueThresholdLow)
  cv.CreateTrackbar('h_hueThreshold',
                    proc_win_name,
                    initHueThreshold,
                    255,
                    skin_detector.setHueThresholdHigh)
  cv.CreateTrackbar('l_intensityThreshold',
                    proc_win_name,
                    initIntensityThreshold,
                    255,
                    skin_detector.setIntensityThresholdLow)
  cv.CreateTrackbar('h_intensityThreshold',
                    proc_win_name,
                    initIntensityThreshold,
                    255,
                    skin_detector.setIntensityThresholdHigh)

  session = ImageProcessSession(skin_detector)
  while True:
    k = cv.WaitKey(msdelay)
    k = chr(k) if k > 0 else 0
    if handle_keyboard(k) < 0:
        break
    bgrimg = cv.QueryFrame(cam)
    if not bgrimg:
        break
    cv.Flip(bgrimg, None, 1)
    contours = session.process(bgrimg)

    img = cv.CreateImage((bgrimg.width, bgrimg.height), 8, 3)
    if contours:
        x, y, r, b = im.find_max_rectangle(contours)
        cv.Rectangle(img, (x,y), (r, b), im.color.RED)
        cv.DrawContours(img, contours, im.color.RED, im.color.GREEN, 1,
            thickness=3)

    cv.ShowImage(proc_win_name, img)


if __name__=='__main__':
  mainLoop()
