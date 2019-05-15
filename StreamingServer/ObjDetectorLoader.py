from ObjectDetector.models import *
from ObjectDetector.utils.utils import *

import torch
import threading

import time
import datetime
import sys

import cv2
from ObjDetectorInfo import *
import torch.multiprocessing as mp
from multiprocessing import Process
from multiprocessing import Queue as queue

from queue import Queue, LifoQueue
from threading import Thread

def rescale(img, inp_dim):
    img_h, img_w = img.shape[:2]
    w, h = inp_dim
    scale_rate = min(w/img_w, h/img_h)
    new_w = int(img_w * scale_rate)
    new_h = int(img_h * scale_rate)
    newimg = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    canvas = np.full((h,w,3), fill_value=255)
    h_shift = (h-new_h)//2
    w_shift = (w-new_w)//2
    canvas[h_shift:h_shift+new_h, w_shift:w_shift+new_w,:] = newimg
    canvas = canvas/255.

    return (img_h, img_w), canvas


def imageToTensor(img):
    imgTensor = torch.from_numpy(img)
    imgTensor = imgTensor.unsqueeze(0)
    imgTensor = imgTensor.permute(0,3,1,2)
    return imgTensor

def preprocess_img(frame,size):
    img_size, img = rescale(frame,(size, size))
    imgTensor = imageToTensor(img)
    return img_size, imgTensor

class ObjDetectorQ:
    def __init__(self, queueSize=50):
#        self.Q = mp.Queue(maxsize=queueSize)
        self.Q = Queue(maxsize = queueSize)
    def push(self, item):
        self.Q.put(item)
    def getitem(self):
        return self.Q.get()
    def length(self):
        return self.Q.qsize()
        
class ObjDetectorLoader:
    def __init__(self,  queueSize=1024):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #set up mode
        objDetectorInfo = ObjDetectorInfo()
        self.inputQ = ObjDetectorQ()

        self.objDetectorModel = Darknet(objDetectorInfo.model_def, img_size=objDetectorInfo.img_size).to(device)
        self.objDetectorModel.share_memory()
        self.objDetectorModel.eval()

        if objDetectorInfo.weights_path.endswith(".weights"):
            #Load darknet weights
            self.objDetectorModel.load_darknet_weights(objDetectorInfo.weights_path)
        else:
            self.objDetectorModel.load_state_dict(torch.load(objDetectorInfo.weights_path))
        
        obj_classes = load_classes(objDetectorInfo.class_path)
        self.classes = obj_classes
        self.batchSize = 1
        self.inputSize = objDetectorInfo.img_size

        self.outputQ = mp.Queue(maxsize=queueSize)
    def start(self):
#        p = mp.Process(target=self.run, args=())
#        p.daemon = True
#        p.start()
        t = Thread(target=self.run, args=())
        t.start()
        t.join()
        return self

    def run(self):
        conf_thres = 0.8
        nms_thres = 0.4
        prev_time = time.time()
        frame = self.inputQ.getitem()
        
        #Configure input
        img_size, img = preprocess_img(frame,self.inputSize)
        Tensor = torch.cuda.FloatTensor if torch.cuda.is_available else torch.FloatTensor
        input_img = Variable(img.type(Tensor))

        with torch.no_grad():
            detections = self.objDetectorModel(input_img)
            detections = non_max_suppression(detections, conf_thres, nms_thres)
        
        current_time = time.time()
        #inference_time = datetime.timedelta(seconds=current_time - prev_time)
        inference_time = current_time-prev_time
        print("\t Inference Time: %s" %(inference_time))
        prev_time = current_time

        detections = detections[0]
        results = []
        if detections is not None:
            detections = rescale_boxes(detections, 416, img_size)
            unique_labels = detections[:,-1].cpu().unique()
            n_cls_preds = len(unique_labels)
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
                bbox_label = [x1, y1, x2, y2, self.classes[int(cls_pred)]]
                results.append(bbox_label)

        self.outputQ.put(results)


