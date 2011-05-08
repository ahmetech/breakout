'''
    Gesture Combination Authentication Program submodule skin detector

    @date: Feb. 02, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv
import im
import face
from constants import SDC

class SkinDetector(object):
  """A Skin Detector Class"""
  def __init__(self):
    self.calibrating = False
    self.storage=cv.CreateMemStorage(0)
    self.v_low = SDC.GSD_INTENSITY_LT
    self.v_high = SDC.GSD_INTENSITY_UT
    self.h_low = SDC.GSD_HUE_LT
    self.h_high = SDC.GSD_HUE_UT

  def checkRange(self, src, lowBound, highBound):
    size = im.size(src)
    mask = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    gt_low = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.CmpS(src, lowBound, gt_low, cv.CV_CMP_GT)
    lt_high = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.CmpS(src, highBound, lt_high, cv.CV_CMP_LT)
    cv.And(gt_low, lt_high, mask)
    return mask

  def toggle_calibrate(self):
    self.calibrating = self.calibrating ^ True

  def segment(self, bgrimg):
    segmented = cv.CreateImage(im.size(bgrimg), bgrimg.depth, bgrimg.nChannels)
    cv.PyrSegmentation(bgrimg, segmented, self.storage, 3, 188, 60)
    return segmented

  def setHueThresholdLow(self, hueThreshold):
    self.h_low = hueThreshold
    print self.h_low, self.h_high

  def setHueThresholdHigh(self, hueThreshold):
    self.h_high = hueThreshold
    print self.h_low, self.h_high

  def setIntensityThresholdLow(self, intensityThreshold):
    self.v_low = intensityThreshold
    print self.v_low, self.v_high

  def setIntensityThresholdHigh(self, intensityThreshold):
    self.v_high = intensityThreshold
    print self.v_low, self.v_high

  def detectSkin(self, bgrimg):
    img_temp = cv.CreateImage(im.size(bgrimg), 8, 3)
    cv.Smooth(bgrimg, img_temp, cv.CV_GAUSSIAN, 5, 5)
    for i in range(3): cv.Smooth(img_temp, img_temp, cv.CV_GAUSSIAN, 5, 5)
    #cv.ShowImage("Capture from camera", img_temp)

    skin = self._detectSkin(img_temp)
    return skin

  def _detectSkin(self, bgrimg):
    #hsvimg = im.bgr2hsv(bgrimg)
    hsvimg = cv.CreateImage((bgrimg.width, bgrimg.height), 8, 3)
    cv.CvtColor(bgrimg, hsvimg, cv.CV_RGB2HSV)
    #h,s,v = im.split3(bgrimg)
    skin_mask = cv.CreateImage((bgrimg.width, bgrimg.height), 8, 1)
    low = (self.h_low, self.v_low, 0)
    high = (self.h_high, self.v_high, 256)
    cv.InRangeS(hsvimg, low, high, skin_mask) 
    #cv.ShowImage("inrange", skin_mask)
     
    face_mask = face.blockfacemask(bgrimg)
    cv.And(skin_mask,  face_mask, skin_mask)
    #h_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    #s_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    #print self.v_low, self.v_high, self.h_low, self.h_high
    #s_mask = self.checkRange(s, self.v_low, self.v_high)
    #h_mask = self.checkRange(h, self.h_low, self.h_high)    
    #cv.And(h_mask, s_mask, skin_mask)

    return skin_mask
