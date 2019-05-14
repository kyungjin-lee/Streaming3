import socket
import cv2
from optparse import OptionParser
import sys
from rtp import RTP
import datetime
from Server import Server
from TestServer import TestServer
import argparse
import torch
import torch.multiprocessing as mp

MAX_RTP_SEQ_NUM = 65535

def run_video(input_folder):
    TestServer(input_folder).run()

def run_streaming(objDetectorInfo, alphaPoseInfo):

    server_addr = ('', 554)
    rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rtspSocket.bind(server_addr)
    print("RTSP listening client request...")
    rtspSocket.listen(5)

    while True:
        clientInfo = {}
        clientInfo['rtspSocket'] = rtspSocket.accept()
        Server(clientInfo, objDetectorInfo, alphaPoseInfo).run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_type", type=str, default="video", help="input type either video or streaming")
    parser.add_argument("--input_folder", type=str, default="data/samples", help="path to dataset")

    opt = parser.parse_args()
    
    if opt.input_type == "video":
        run_video(opt.input_folder)
    elif opt.input_type == "streaming":
        run_streaming()
    else:
        print("Wrong input type, video or streaming") 
    
