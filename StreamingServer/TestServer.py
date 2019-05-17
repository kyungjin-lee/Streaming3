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

from threading import Thread
from queue import Queue

from multideepQ import PriorityQueue, VideoStreamQueue

from AlphaPoseLoader import *
from threading import Thread

class TestServer:
    
    def __init__(self, input_folder):
        self.input_folder = input_folder
        self.VideoStreamQueue = VideoStreamQueue()
        self.PriorityQueue = PriorityQueue()
      
#        self.objDetectorQ = ObjDetectorQ()
#        self.alphaPoseQ = AlphaPoseQ()
        self.objDetector = ObjDetectorLoader()
        self.alphaPose = AlphaPoseLoader()
      
    def run(self):
        self.VideoStreamQueue.start(self.input_folder)
        self.PriorityQueue.start(self.VideoStreamQueue)
        self.roundrobin()
#        p = mp.Process(target=self.feedDnn, args=())
#        p.daemon=True
#        p.start() 
        #t = Thread(target=self.feedDnn, args=())
        #t.daemon = True
        #t.start()  
 #       self.objDetectorProcessor.start()
 #       self.alphaPoseProcessor.start()
    def roundrobin(self):
        obj_prev = time.time()
        alpha_prev = time.time()
        while True:
            q_time = time.time()
            mId, frame = self.PriorityQueue.getitem()
            if mId ==0:
                obj_cur = time.time()
                self.objDetector.inputQ.push(frame)
                self.objDetector.run()
                print("1. ObjDetector: ", obj_cur - obj_prev)
                obj_prev = obj_cur
            else:
                alpha_cur = time.time()
                self.alphaPose.inputQ.push(frame)
                alpha_run_time = time.time()
                self.alphaPose.run()
                print("2. AlphaPose: ", alpha_cur - alpha_prev)
                alpha_prev = alpha_cur
            print("Run time: ", time.time()-q_time)



