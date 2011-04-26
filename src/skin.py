'''
    Gesture Combination Authentication Program submodule skin detector

    @date: Feb. 02, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv
import im
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

  def setHueThreshold(self, hueThreshold):
    self.h_low, self.h_high = max(hueThreshold-55,0), min(hueThreshold+55,255)
    print self.h_low, self.h_high

  def setIntensityThreshold(self, intensityThreshold):
    self.v_low, self.v_high = max(intensityThreshold-40,0), min(intensityThreshold+40,255)
    print self.v_low, self.v_high

  def detectSkin(self, bgrimg):
    img_temp = cv.CreateImage(im.size(bgrimg), bgrimg.depth, bgrimg.nChannels)
    #cv.SaveImage("original.png", bgrimg)
    cv.Smooth(bgrimg, img_temp, cv.CV_MEDIAN, 15)#, 0, 20, 20)
    #cv.SaveImage("smooth.png", img_temp)
    cv.ShowImage("Capture from camera", img_temp)

    #skin_o = self._detectSkin(bgrimg)
    #cv.SaveImage("skin_o.png", skin_o)
    skin = self._detectSkin(img_temp)
    #cv.SaveImage("skin_s.png", skin)
    return skin

  def _detectSkin(self, bgrimg):
    hsvimg = im.bgr2hsv(bgrimg)
    h,s,v = im.split3(bgrimg)
    skin_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    h_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    v_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)

    v_mask = self.checkRange(v, self.v_low, self.v_high)
    h_mask = self.checkRange(h, self.h_low, self.h_high)    
    cv.And(h_mask, v_mask, skin_mask)

    return skin_mask
