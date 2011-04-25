'''
Created on Sep 15, 2010

@author: diego
'''

import cv

thresh1=0
thresh2=0

def on_trackbar2(val):
    global thresh2
    thresh2=val

def on_trackbar(val):
    global thresh1
    thresh1=val



def main():
    global thresh1,thresh2
    capture = cv.CaptureFromCAM(0)
    cv.NamedWindow("capture")
    cv.NamedWindow("Segmentation")
    cv.CreateTrackbar("thresh2", "Segmentation", thresh2, 255, on_trackbar2)
    cv.CreateTrackbar("thresh1", "Segmentation", thresh1, 255, on_trackbar)
    storage=cv.CreateMemStorage(0)
    frameAux = cv.QueryFrame(capture)
    segmented = cv.CreateImage(cv.GetSize(frameAux), 8, 3)
    while(True):
        frame = cv.QueryFrame(capture)
        cv.ShowImage("capture", frame)
    #    cv.PyrMeanShiftFiltering(frame, segmented, 100, 50)
        print thresh1, thresh2
        cv.PyrSegmentation(frame, segmented, storage, 3, thresh1, thresh2)
        cv.ShowImage("Segmentation", segmented)
        cv.WaitKey(100)


main()