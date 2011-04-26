import cv
import sys
import time
import im


h_lower, h_upper, s_lower, s_upper = (94, 104, 82, 167)
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 255, 0)

def on_track_bar_hlow(pos):
    global h_lower
    h_lower = pos

def on_track_bar_hhigh(pos):
    global h_upper
    h_upper = pos

def on_track_bar_slow(pos):
    global s_lower
    s_lower = pos

def on_track_bar_shigh(pos):
    global s_upper
    s_upper = pos

def get_hand(img):
    global h_lower, h_upper, s_lower, s_upper
    storage = cv.CreateMemStorage(0)
    contours, hull, max_contours, max_hull = (0, 0, 0, 0)
    max_rect = (1, 1, 100, 100)
    dst = cv.CreateImage((img.width, img.height), 8, 3)
    hsv = cv.CreateImage((img.width, img.height), 8, 3)
    frame = cv.CreateImage((img.width, img.height), 8, 1)
    con = cv.CreateImage((img.width, img.height), 8, 1)
    cv.Zero(con)
    cv.Smooth(img, dst, cv.CV_GAUSSIAN, 5, 5)
    for i in range(3): cv.Smooth(dst, dst, cv.CV_GAUSSIAN, 5, 5)
    cv.CvtColor(dst, hsv, cv.CV_RGB2HSV)
    cv.InRangeS(hsv, (h_lower, s_lower, 0), (h_upper, s_upper, 256), frame) 
    kernel = cv.CreateStructuringElementEx(3, 3, 0, 0, cv.CV_SHAPE_RECT)
    #cv.MorphologyEx(frame, frame, None, kernel, cv.CV_MOP_CLOSE , 7)
#    cv.MorphologyEx(frame, frame, None, kernel, cv.CV_MOP_OPEN , 3)
    contours = im.find_contours(frame)
    hull = im.find_convex_hull(contours)
    print contours

    #max_hull_area, max_contour_area = (0, 0)
    #print "xxxxxxxx"
    #contour = contours.h_next()
    #print "........"
    #while (contour != 0):
    #    hull = cv.ConvexHull2(contour, storage, cv.CV_CLOCKWISE, 1);
    #    maxv = cv.ContourArea(hull)
    #    contour = contour.h_next()
    cv.DrawContours(con, contours, red, blue, 1, 3, 8)
    

    cv.ShowImage("result", con)

def main():
    print "hello world"
    capture = cv.CreateCameraCapture(0)
    cv.NamedWindow("test", 1)
    cv.NamedWindow("result", 1)
    global h_lower, h_upper, s_lower, s_upper
    cv.CreateTrackbar("hlow", "result", h_lower, 256, on_track_bar_hlow)
    cv.CreateTrackbar("hhigh", "result", h_upper, 256, on_track_bar_hhigh)
    cv.CreateTrackbar("slow", "result", s_lower, 256, on_track_bar_slow)
    cv.CreateTrackbar("shigh", "result", s_upper, 256, on_track_bar_shigh)
    while True:
        image = cv.QueryFrame(capture)
        get_hand(image)
        cv.ShowImage("test", image)
        if(cv.WaitKey(10) != -1):
            break


if __name__ == '__main__':
    main()
