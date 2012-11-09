#!/usr/bin/env python
'''
luminance-scope.py
Copyright (C) 2012 Magnus Skjegstad 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

from optparse import OptionParser

# default values
updateinterval = 30
fps = 30.
cameraindex = 0
lumthresh = 245

parser = OptionParser()                                                                                                                                                           
parser.add_option("-f", "--file", help="File name.", dest="file")                                                                                                                 
parser.add_option("-t", "--thresh", help="Set luminance threshold 0-255. Lower luminance is ignored (default=" + str(lumthresh), dest="threshold")
parser.add_option("-c", "--camera", help="Process data from camera with this index (default=" + str(updateinterval) + ")", dest="cameraindex")
parser.add_option("-s", "--show", help="Show processing window.", dest="show")                                                                                                         
parser.add_option("-u", "--update", help="Graph update interval in frames. Increase this to reduce processing time (default=" + str(updateinterval) + ").", dest="update_interval")
parser.add_option("-p", "--fps", help="Try to maintain this framerate from webcam. Ignored when reading from file (default=" + str(fps) + ").", dest="fps")
(options, args) = parser.parse_args() 

if options.threshold != None:
    lumthresh = int(options.threshold)

print "# Luminance threshold is ",lumthresh

if options.file != None and options.fps != None:
    print "# FPS set manually, but will be overridden by frame rate from input file"
else:
    if options.fps != None:
        fps = round(float(options.fps))
        print "# FPS set to", fps

if options.file != None and options.cameraindex != None:
    parser.error("Data cannot be processed from file and camera at the same time.")

if options.file == None and options.cameraindex == None:
    print("# Neither file or camera index specified. Trying to use camera 0 ...")
    options.cameraindex = 0

if options.update_interval != None:
    updateinterval = int(options.update_interval)

print "# Real time graph will be updated every",updateinterval,"frame(s)"

print "# Importing OpenCV..."
import cv, cv2

if options.cameraindex != None:
    capture = cv.CreateCameraCapture(int(options.cameraindex))

    capturefps = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS)
    if capturefps != 0:
        fps = capturefps
        print "# Trying to maintain target FPS of ", fps
    else:
        print "# Camera has unknown frame rate. Falling back to", fps, " fps"
else:
    parser.error("File input not supported yet. Aborting...")

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import sys
import os
import traceback
import Queue
from threading import Thread
from scipy.signal import butter, lfilter
from time import sleep
from time import time

# Try to maintain frame rate by buffering frames in separate thread
q = Queue.Queue()
stopThreads = False
def enqueuer():
    ts = time()
    while not stopThreads:
        frame = cv.QueryFrame(capture)
        if frame == None:
            continue 
        q.put(frame, False)
        sleep( (1. / fps) - (time() - ts))
        ts = time()

print "# Starting OpenCV capture"

counter = 0

yuvimg = None
threshimg = None

try:
    maskavglen = 30

    meanarray = np.zeros(400)
    plt.ion() # real time updates
    line, = plt.plot(meanarray,  "-")
    plt.ylim([0,2])
    plt.show()

    # Start queue thread
    t = Thread(target = enqueuer)
    t.daemon = True
    t.start()

    starttime = time()

    while True:
        # check if queue is processed fast enough
        if (q.qsize() > updateinterval*2 and counter > updateinterval*2):
            print "# Warning: Unable to process frames from queue fast enough - try to increase graph update interval with -u (queue length: ", q.qsize(), ")"
        
        # Get next frame from queue
        frame = q.get()
        q.task_done()
        
        counter = counter + 1    

        # Create temporary images for yuv and threshold
        if threshimg == None:
            threshimg = cv.CreateImage((frame.width,frame.height), 8, 1)

        if yuvimg == None: 
            yuvimg = cv.CreateImage((frame.width,frame.height), 8, 3)
        
        # Convert image to YUV
        cv.CvtColor(frame, yuvimg, cv.CV_BGR2YCrCb)
        
        # Filter out pixels with more than 245 luminance
        cv.InRangeS(yuvimg, cv.Scalar(lumthresh, 0, 0), cv.Scalar(255, 255, 255), threshimg)

        # Convert to cv2-format and reduce noise
        bwimg = np.asarray(threshimg[:,:])
        cv2.equalizeHist(bwimg, bwimg)
        bwimg = cv2.GaussianBlur(bwimg, (9,9), 2) 

        if options.show: 
            cv2.imshow("Processed image", np.asarray(bwimg[:,:]))

        # Add to graph
        meanarray = np.roll(meanarray, 1)
        meanarray[0] = cv2.mean(bwimg)[0]

        # Update pyplot every [updateinterval] frame
        if counter % updateinterval == 0:
            # Calculate processing fps
            time_per_frame = (time() - starttime) / updateinterval
            starttime = time()
            realfps = 1. / time_per_frame 

            mina = np.min(meanarray)
            maxa = np.max(meanarray)

            print "# frame:",counter,"fps:",realfps, "qlen:", q.qsize(), "miny:", mina, "maxy:", maxa

            # set y axis to 10 % higher than max/min
            plt.ylim([mina - (maxa-mina)*0.1, maxa + (maxa-mina)*0.1])
            # set data
            line.set_ydata(meanarray)
            # draw on screen
            plt.draw()

        if cv.WaitKey(20) >= 0:
            break

except:
    traceback.print_exc()
    raise
finally:
    stopThreads = True

print "# done"

