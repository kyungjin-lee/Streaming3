import torch.multiprocessing as mp
from multiprocessing import Process
from multiprocessing import Queue as queue

from threading import Thread
from queue import Queue
import torch
from AlphaPose.yolo.preprocess import prep_frame
import cv2

class VideoStreamQueue:
    def __init__(self, queueSize = 1024):
        self.Q = mp.Queue(maxsize = queueSize)
    def start(self, video_path):
        p = mp.Process(target=self.run, args=[video_path])
        p.daemon = True
        p.start()
        return self
    def run(self, video_path):
        self.stream = cv2.VideoCapture(video_path)
        assert self.stream.isOpened(), 'Cannot capture source'
        while(self.stream.isOpened()):
            (grabbed, frame) = self.stream.read()
            if grabbed == True:
                self.Q.put(frame)
            else:
                break
    def getitem(self):
        return self.Q.get()
    def length(self):
        return self.Q.qsize()

class PriorityQueue:
    def __init__(self, queueSize = 1024):
        self.Q = mp.Queue(maxsize = queueSize)
#        self.Q = Queue(maxsize = queueSize)
    def start(self, inputQ):
#        t = Thread(target=self.readframe, args=[video_path])
#        t.daemon = True
#        t.start()
        p = mp.Process(target=self.run, args=([inputQ]))
        p.daemon = True
        p.start()
        return self

    def run(self, inputQ):
        mId = 0
        while True:
            frame = inputQ.getitem()
            self.Q.put((mId, frame))
            mId = 1-mId

    def getitem(self):
        return self.Q.get()

    def length(self):
        return self.Q.qsize()   
