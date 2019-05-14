from __future__ import division
from ObjectDetector.models import *
from ObjectDetector.utils import *
from ObjDetectorLoader import *

from os import listdir
from os.path import isfile, join
import time, datetime
import sys, threading, socket
import struct
import cv2

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

from rtp import RTP
from MultiDeep import run_multideep

from threading import Thread
from queue import Queue

from multideepQ import PriorityQueue

from AlphaPoseLoader import *
from threading import Thread

class TestServer:
    
    def __init__(self, input_folder):
        self.input_folder = input_folder
        self.PriorityQueue = PriorityQueue()
      
#        self.objDetectorQ = ObjDetectorQ()
#        self.alphaPoseQ = AlphaPoseQ()
        self.objDetector = ObjDetectorLoader()
        self.alphaPose = AlphaPoseLoader()
      
    def run(self):
        self.PriorityQueue.start(self.input_folder)
        self.feedDnn()
#        p = mp.Process(target=self.feedDnn, args=())
#        p.daemon=True
#        p.start() 
        #t = Thread(target=self.feedDnn, args=())
        #t.daemon = True
        #t.start()  
 #       self.objDetectorProcessor.start()
 #       self.alphaPoseProcessor.start()
    def feedDnn(self):
        frame = self.PriorityQueue.getitem()
#        self.objDetector.inputQ.push(frame)
        self.alphaPose.inputQ.push(frame)
#        self.objDetector.inputQ.push(frame)
        self.objDetector.run(frame)
        self.alphaPose.run()
#        self.alphaPoseQ.push(frame)
        
#run_multideep(self.PriorityQueue, self.objDetectorModel, self.alphaPoseModel)




#         path = self.input_folder
#         onlyfiles = [f for f in listdir(path) if isfile(join(path,f))]
#         for n in range(0, len(onlyfiles)):
#             print("Image name: ", join(path,onlyfiles[n]))
#             frame = cv2.imread(join(path,onlyfiles[n]))
#             run_multideep(frame, self.objDetectorModel)
##        threading.Thread(target=self.recvRtspRequest).start()
#        cap = cv2.VideoCapture(self.input_folder)
#        assert cap.isOpened(), 'Cannot capture source. Cannot find video file'
#        while cap.isOpened():
#            ret, frame = cap.read()
#            if ret:
#                run_multideep(frame,self.objDetectModel)
