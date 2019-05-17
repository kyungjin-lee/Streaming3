import torch.multiprocessing as mp
from multiprocessing import Process
from multiprocessing import Queue as queue
from queue import Queue
#for Alphaposeinfo
#for AlphaPoseQ
from AlphaPose.yolo.preprocess import prep_frame


import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.utils.data
import numpy as np
from AlphaPose.dataloader import DetectionLoader, DetectionProcessor, Mscoco
from AlphaPose.SPPE.src.main_fast_inference import *
from AlphaPose.SPPE.src.utils.eval import *

import ntpath
import os
import sys
import time
from AlphaPose.fn import getTime,vis_frame
import cv2
from AlphaPose.pPose_nms import pose_nms


from threading import Thread

class AlphaPoseInfo:
    def __init__(self):
        self.dataset = 'coco'
        self.fast_inference = True
        self.nThreads = 30
        self.sp = True
        self.use_pyranet = True
        self.inputResH = 320
        self.inputResW = 256
        self.outputResH = 80
        self.outputResW = 64
        self.scale = 0.25
        self.rotate = 30
        self.hmGauss = 1
        self.baseWidth = 9
        self.cardinality = 5
        self.nResidual = 1
        self.net = 'res152'
        self.mode = "normal"
        self.inp_dim = 608
        self.confidence = 0.05
        self.nms_thesh = 0.6
        self.num_classes = 80
class AlphaPoseQ:
    def __init__(self, queueSize=50):
#        self.Q = mp.Queue(maxsize=queueSize)
        self.Q = Queue(maxsize=queueSize)
    def push(self,item,inputSize=608):
        frame = item
        img, orig_img, im_dim_list = prep_frame(frame, inputSize)
        with torch.no_grad():
            im_dim_list = torch.FloatTensor(im_dim_list).repeat(1,2)
        self.Q.put((img,[orig_img],["temp"],im_dim_list))
    def getitem(self):
        return self.Q.get()
    def length(self):
        return self.Q.qsize()        

class AlphaPoseLoader:
    def __init__(self,queueSize=1024):
        self.alphaPoseInfo = AlphaPoseInfo()
        self.inputQ = AlphaPoseQ()
        self.det_loader = DetectionLoader(self.alphaPoseInfo, self.inputQ, batchSize=1)
        self.det_processor = DetectionProcessor(self.alphaPoseInfo, self.det_loader)
        self.pose_dataset = Mscoco(self.alphaPoseInfo)

        if self.alphaPoseInfo.fast_inference:
            self.pose_model = InferenNet_fast(4 * 1 +1, self.pose_dataset)
        else:
            self.pose_model = InferenNet(4*1+1, self.pose_dataset)
        self.pose_model.cuda()
        self.pose_model.eval()

        self.outputQ = Queue(maxsize=queueSize)
        self.startTime = time.time()
    def start(self):
#        p = mp.Process(target=self.run, args=())
#        p.daemon = True
#        p.start()
        t = Thread(target=self.run, args=())
        t.start()
        t.join()
        return self

    def run(self):
        startTime = time.time()
        det_results = self.det_loader.update()
        self.det_processor.update(det_results)
        runtime_profile = {
            'dt': [],
            'pt': [],
            'pn': []
        }
        start_time = getTime()
        with torch.no_grad():
            (inps, orig_img, im_name, boxes, scores, pt1, pt2) = self.det_processor.read()
            if orig_img is None:
                return
            ckpt_time, det_time = getTime(start_time)
            runtime_profile['dt'].append(det_time)
            datalen = inps.size(0)
            batchSize = 1
            num_batches = datalen//batchSize
            
            hm = []
            for j in range(num_batches):
                inps_j = inps[j*batchSize:min((j+1)*batchSize, datalen)].cuda()
                hm_j = self.pose_model(inps_j)
                hm.append(hm_j)
            hm = torch.cat(hm)
            ckpt_time, pose_time = getTime(ckpt_time)
            runtime_profile['pt'].append(pose_time)
            hm = hm.cpu().data
            ckpt_time, post_time = getTime(ckpt_time)
            runtime_profile['pn'].append(post_time)
            self.outputQ.put((boxes, scores, hm, pt1, pt2))
            preds_hm, preds_img, preds_scores = getPrediction(hm, pt1, pt2, 320, 256, 80, 64)
            result = pose_nms(boxes, scores, preds_img, preds_scores)
            result = {
                'imgname': 1,
                'result': result
            }
            #finalimg = vis_frame(orig_img, result)
            #cv2.imwrite("finalresult.png", finalimg)
            endTime = time.time()
            print("\tAlphaPose Inference Time : ", endTime-startTime)
            self.startTime = endTime

