'''
   Face Detection Submodule

   @date: May, 2011.
   @author: Jie Huang and Shao-Chuan Wang
'''

import cv
import im

cascade = cv.Load('haarcascade_frontalface_alt.xml')
def detect_faces(bgrimg):
    grayscale = im.bgr2gray(bgrimg)
    # create storage
    storage = cv.CreateMemStorage(0)
 
    # equalize histogram
    cv.EqualizeHist(grayscale, grayscale)
 
    # detect objects
    faces = cv.HaarDetectObjects(cv.GetMat(grayscale), cascade, storage, 1.2, 2, 0, (100, 100))
    
    if faces:
        return [f[0] for f in faces]
    else:
        return None

lastrects = None
def blockfacemask(bgrimg):
    global lastrects
    rects = detect_faces(bgrimg)
    newimg = im.newgray(bgrimg)
    cv.Set(newimg, 255)
    if rects:
      lastrects = rects
    else:
      rects = lastrects
    if rects:
      for rect in rects:
        cv.SetImageROI(newimg, rect)
        cv.Set(newimg, 0)
        cv.ResetImageROI(newimg)
    return newimg
