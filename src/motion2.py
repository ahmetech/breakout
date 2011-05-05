#!/usr/bin/python
import urllib2
import sys
import time
from math import cos, sin
import cv
import im


class MotionUtility:

    def __init__(self):
        self.CLOCKS_PER_SEC = 0.5
        self.MHI_DURATION = 1
        self.MAX_TIME_DELTA = 0.5
        self.MIN_TIME_DELTA = 0.05
        self.N = 3
        self.buf = range(10) 
        self.last = 0
        self.mhi = None # MHI
        self.orient = None # orientation
        self.mask = None # valid orientation mask
        self.segmask = None # motion segmentation map
        self.storage = None # temporary storage
        self.timestamp = None
        self.silh = None
        self.test = None


    def get_motion_mask(self, img, diff_threshold=30):
        self.timestamp = time.clock() / self.CLOCKS_PER_SEC # get current time in seconds
        size = cv.GetSize(img) # get current frame size
        idx1 = self.last
        if not self.mhi or cv.GetSize(self.mhi) != size:
            for i in range(self.N):
                self.buf[i] = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
                cv.Zero(self.buf[i])
            self.mhi = cv.CreateImage(size,cv. IPL_DEPTH_32F, 1)
            cv.Zero(self.mhi) # clear MHI at the beginning
            self.orient = cv.CreateImage(size, cv.IPL_DEPTH_32F, 1)
            self.segmask = cv.CreateImage(size, cv.IPL_DEPTH_32F, 1)
            self.mask = cv.CreateImage(size, 8, 1)
            self.test = cv.CreateImage(size, 8, 3)
        cv.CvtColor(img, self.buf[self.last], cv.CV_BGR2GRAY) # convert frame to grayscale
        #self.buf[self.last] = cv.CloneImage(img)
        idx2 = (self.last + 1) % self.N # index of (last - (N-1))th frame
        self.last = idx2
        self.silh = self.buf[idx2]
        cv.AbsDiff(self.buf[idx1], self.buf[idx2], self.silh) # get difference between frames
        cv.Threshold(self.silh, self.silh, diff_threshold, 1, cv.CV_THRESH_BINARY) # and threshold it
        cv.UpdateMotionHistory(self.silh, self.mhi, self.timestamp, self.MHI_DURATION) # update MHI
        cv.CvtScale(self.mhi, self.mask, 255./self.MHI_DURATION,
                    (self.MHI_DURATION - self.timestamp)*255./self.MHI_DURATION)
        #cv.ShowImage("motion mask", self.mask)
        max_rect = self.segment_motion()
        return self.mask

    def segment_motion(self):
        min_area = 100
        size = cv.GetSize(self.mask) # get current frame size
        temp = cv.CloneImage(self.mask) 
        cv.CalcMotionGradient(self.mhi, temp, self.orient, self.MAX_TIME_DELTA,
                self.MIN_TIME_DELTA, 3)
        #cv.ShowImage("orient", self.orient);
        if not self.storage:
            self.storage = cv.CreateMemStorage(0)
        seq = cv.SegmentMotion(self.mhi, self.segmask, self.storage, self.timestamp,
                self.MAX_TIME_DELTA)
        #cv.ShowImage("segmask", self.segmask)

        max = 0
        max_idx = -1
        for i in range(len(seq)):
            (area, value, comp_rect) = seq[i]
            if area > max:
                max = area
                max_idx = i
        if max_idx == -1: 
            cv.Zero(self.mask)
            return

        (area, value, comp_rect) = seq[max_idx]
        if (area < 100):
            cv.Zero(self.mask)
            return

        cv.Zero(self.mask)
        cv.Rectangle(self.mask, (comp_rect[0], comp_rect[1]), (comp_rect[0] +
            comp_rect[2], comp_rect[1] + comp_rect[3]), (255,255,255),
            cv.CV_FILLED)


"""
        (area, value, comp_rect) = seq[max_idx]
        if comp_rect[2] + comp_rect[3] > 100: # reject very small components
            color = cv.CV_RGB(255, 0,0)
            silh_roi = cv.GetSubRect(self.silh, comp_rect)
            mhi_roi = cv.GetSubRect(self.mhi, comp_rect)
            orient_roi = cv.GetSubRect(self.orient, comp_rect)
            mask_roi = cv.GetSubRect(self.mask, comp_rect)

            angle = 360 - cv.CalcGlobalOrientation(orient_roi, mask_roi, mhi_roi, timestamp, MHI_DURATION)
            count = cv.Norm(silh_roi, None, cv.CV_L1, None) # calculate number of points within silhouette ROI
            if count < (comp_rect[2] * comp_rect[3] * 0.05):
                return

            magnitude = 30
            center = ((comp_rect[0] + comp_rect[2] / 2), (comp_rect[1] + comp_rect[3] / 2))
            cv.Circle(dst, center, cv.Round(magnitude*1.2), color, 3, cv.CV_AA, 0)
            cv.Line(dst,
                    center,
                    (cv.Round(center[0] + magnitude * cos(angle * cv.CV_PI / 180)),
                     cv.Round(center[1] - magnitude * sin(angle * cv.CV_PI / 180))),
                    color,
                    3,
                    cv.CV_AA,
                    0)

if __name__ == "__main__":
    motion = 0
    capture = 0

    capture = cv.CreateCameraCapture(0)

    if not capture:
        print "Could not initialize capturing..."
        sys.exit(-1)
        
    cv.NamedWindow("Motion", 1)
    while True:
        image = cv.QueryFrame(capture)
        if(image):
            if(not motion):
                    motion = cv.CreateImage((image.width, image.height), 8, 3)
                    cv.Zero(motion)
                    #motion.origin = image.origin
            update_mhi(image, motion, 30)
            cv.ShowImage("Motion", motion)
            if(cv.WaitKey(10) != -1):
                break
        else:
            break
    cv.DestroyWindow("Motion")
"""
