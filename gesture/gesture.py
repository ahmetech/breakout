'''
    Gesture Combination Authentication Program submodule gesture.

    @date: Feb. 02, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
from constants import GAC
import motion
import im

class Gesture(object):
    def __init__(self, type_, timing=''):
        self.timing = timing
        self.type_ = type_

    def __repr__(self):
        return self.timing + ' ' + self.type_

    def __eq__(self, obj):
        return self.type_ == obj.type_ and self.timing == obj.timing

    def hasMeaning(self):
        return self.type_ != 'Not Sure'

class GestureAnalyzer(object):
    """GestureAnalyzer is responsble for recognizing gesture commands"""
    def __init__(self):
        self.motion = motion.MotionTracker() # currently unused.
        self.gestures_buffer = []
        self.buffer_size = 5

    def recognize(self, contours):
        # using maximal area and convexity defect depths to 
        # recognize between palm and fist.
        x, y, r, b = im.find_max_rectangle(contours)
        max_area, contours = im.max_area(contours)
        print 'area: ', float(max_area)/((r-x)*(b-y))
        hull = im.find_convex_hull(contours)
        mean_depth = 0
        if hull:
          cds = im.find_convex_defects(contours, hull)
          if len(cds) != 0:
              mean_depth = sum([cd[3] for cd in cds])/len(cds)

        if not self.isFist(max_area,
                mean_depth) and not self.isPalm(max_area, mean_depth):
            if self.gestures_buffer:
              self.gestures_buffer.pop(0)
            return Gesture('Not Sure'), max_area, mean_depth

        # The majority of votes in self.gestures_buffer will
        # determine which gesture should be in this frame
        FIST = 0
        PALM = 1
        if self.isFist(max_area, mean_depth):
            self.gestures_buffer.append(FIST)
        elif self.isPalm(max_area, mean_depth):
            self.gestures_buffer.append(PALM)
        self.gestures_buffer = self.gestures_buffer[-self.buffer_size:]
        avg = float(sum(self.gestures_buffer))/self.buffer_size
        if avg > 0.5:
            ges = 'Palm'
        else:
            ges = 'Fist'
        return Gesture(ges, 'Short'), max_area, mean_depth

    def isFist(self, area, depth):
        return GAC.FIST.DEPTH_L < depth < GAC.FIST.DEPTH_U and \
               GAC.FIST.AREA_L  < area  < GAC.FIST.AREA_U

    def isPalm(self, area, depth):
        return GAC.PALM.DEPTH_L < depth < GAC.PALM.DEPTH_U and \
               GAC.PALM.AREA_L  < area  < GAC.PALM.AREA_U

