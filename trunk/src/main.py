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


class Grammar(object):
    def __init__(self, initGrammar=[]):
        self.grammar = initGrammar
        self.repeat_count = 0
        self.not_sure_count = 0
        self.long_threshold = 8
        self.last_ges = gesture.Gesture('Not Sure')
        self.start_ges = gesture.Gesture('Palm', 'Long')

    def __repr__(self):
        return repr(self.grammar)

    def __eq__(self, obj):
        return self.grammar == obj.grammar

    def instantGes(self, ges):
        if ges.hasMeaning():
            self.not_sure_count = 0
            last = self.last_ges
            if last.type_ == ges.type_:
                self.repeat_count += 1
            else:
                self.repeat_count = 0

            if self.repeat_count >= self.long_threshold:
                ges.timing = 'Long'

            if self.grammar:
                if last.type_ == ges.type_:
                    self.grammar[-1] = ges
                else:
                    self.grammar.append(ges)
            else:  # empty grammar needs 'Long Palm' to start to record
                if ges == self.start_ges:
                    self.grammar.append(ges)
            self.last_ges = ges
        else:
            self.not_sure_count += 1
            if self.not_sure_count >= self.long_threshold:
                self.grammar = []
                self.repeat_count = 0

        return self.grammar

class ImageProcessSession(object):
  """ ImageProcessSession is a high level filter manager object.
  """
  def __init__(self, skin_detector):
    self.skin_detector = skin_detector

  def process(self, bgrimg):
    img = self.skin_detector.detectSkin(bgrimg)
    contours = im.find_contours(img)
    return contours



class ImageWriter(object):
    def __init__(self, output_folder='.'):
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        self.id_ = 1
    def write(self, bgrimg):
        fullpath = self.output_folder + os.sep + '%.3d.png' % (self.id_,)
        cv.SaveImage(fullpath, bgrimg)
        self.id_ += 1

def get_input_video_filename():
    if len(sys.argv) > 1 and '-i' in sys.argv:
        i = sys.argv.index('-i')
        return sys.argv[i+1]
    else:
        return ''

def get_grammar_filename():
    if len(sys.argv) > 1 and '-g' in sys.argv:
        i = sys.argv.index('-g')
        return sys.argv[i+1]
    else:
        return ''

def get_output_folder():
    if len(sys.argv) > 1 and '-o' in sys.argv:
        i = sys.argv.index('-o')
        return sys.argv[i+1]
    else:
        return 'out'

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
  skin_detector.setHueThreshold(initHueThreshold)
  skin_detector.setIntensityThreshold(initIntensityThreshold)
  cv.CreateTrackbar('hueThreshold',
                    proc_win_name,
                    initHueThreshold,
                    255,
                    skin_detector.setHueThreshold)
  cv.CreateTrackbar('intensityThreshold',
                    proc_win_name,
                    initIntensityThreshold,
                    255,
                    skin_detector.setIntensityThreshold)

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
