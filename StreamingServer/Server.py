from __future__ import division
from ObjectDetector.models import *
from ObjectDetector.utils.utils import *
from ObjectDetector.utils.datasets import *

import os 
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
def load_objDetectModel(objDetectInfo):
    #Set up model
    model = Darknet(objDetectInfo['obj_model_def'], img_size=416).to(device)

    if objDetectInfo['obj_weights_path'].endswith(".weights"):
        #Load Darknet weights
        model.load_darknet_weights(objDetectInfo['obj_weights_path'])
    else:
        #Load checkpoint weights
        model.load_state_dict(torch.load(objDetectInfo['obj_weights_path']))

    model.eval()

    obj_classes = load_classes(objDetectInfo['obj_class_path'])

    objDetectModel = {}
    objDetectModel['model'] = model
    objDetectModel['obj_class'] = obj_classes
    return objDetectModel


class Server:
    SETUP = 'SETUP'
    OPTIONS = 'OPTIONS'
    ANNOUNCE = 'ANNOUNCE'

    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    OK_200 = 0
    FILE_NOT_FOUND_404 = 1
    CON_ERR_500 = 2

    clientInfo = {}
   
    
    def __init__(self, clientInfo, objDetectInfo):
        self.clientInfo = clientInfo
        self.objDetectInfo = objDetectInfo
        self.rtp_parser = RTP()
        self.data = b''
        self.data_len = 0
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.objDetectModel = load_objDetectModel(self.objDetectInfo)
    
      
    def run(self):
#        threading.Thread(target=self.recvRtspRequest).start()
        self.recvRtspRequest()
    def recvRtspRequest(self):
        """Receive RTSP request from the client"""
        connSocket = self.clientInfo['rtspSocket'][0]
        while True:
            data = connSocket.recv(2048)
            if data:
                print("received data: ", len(data))
                #print ('-'*60+"\nData received\n"+'-'*60)
                self.processRtspRequest(data)

    def processRtspRequest(self, data):
        """Process RTSP request sent from the client."""
        while True:
            self.data += data
            data = b''
            data_len = len(self.data)
            print("data_len: ", data_len)
            if data_len >= 4:
                header = struct.unpack('>ccH',self.data[:4])
                data_len -= 4
            else: break
            print("header[0] : ", header[0])
            if header[0] == b'$':
                exp_len = header[2]

                print("exp_len: ", exp_len)
                if data_len >= exp_len:
                    video_data = self.data[4:4+exp_len]
                    decoded_frame = self.rtp_parser.recv_pkt(video_data)
                    if decoded_frame is not None:
                        print("==============Frame not none=============")
                        run_multideep(decoded_frame,self.objDetectModel)
                        img = cv2.cvtColor(decoded_frame, cv2.COLOR_RGB2BGR)
                        cv2.imshow("preview", img)
                        key = cv2.waitKey(1)
                        if key&0xFF == ord('q'):
                            break
                    print("self.data len before: " , len(self.data))
                    self.data = self.data[4+exp_len:]
                    print("self.data len: " , len(self.data))
                else: break
            else: break

    def replyRtsp(self, code, seq):
        """Send RTSP reply to the client."""
        if code == self.OK_200:
            #print "200 OK"
            reply = ('RTSP/1.0 200 OK\nCSeq: '+seq+'\n').encode()
            connSocket = self.clientInfo['rtspSocket'][0]
            connSocket.send(reply)

        #Error messages
        elif code == self.CON_ERR_500:
            print ("500 Connection Error")
