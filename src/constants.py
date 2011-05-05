'''
    Gesture Combination Authentication Program constants modules.

    @date: Feb. 03, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''

class GACAttributes(object):
    pass

class GAC(object):
    ''' GestureAnalyzer Constants. '''
    FIST = GACAttributes()
    FIST.DEPTH_L = 10.0
    FIST.DEPTH_U = 50.0
    FIST.AREA_L = 17000.0
    FIST.AREA_U = 85000.0

    PALM = GACAttributes()
    PALM.DEPTH_L = 60.0
    PALM.DEPTH_U = 200.0
    PALM.AREA_L = 30000.0
    PALM.AREA_U = 120000.0

class SDC(object):
    ''' Skin SkinDetector Constants. '''
    GSD_HUE_LT = 91
    GSD_HUE_UT = 115
    GSD_INTENSITY_LT = 90
    GSD_INTENSITY_UT = 180
