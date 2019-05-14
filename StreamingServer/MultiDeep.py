from __future__ import division

from ObjectDetector.models import *
from ObjectDetector.utils.utils import *
from ObjectDetector.utils.datasets import *

import os
import sys
import time
import datetime
import argparse

from PIL import Image

import cv2

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable


from threading import Thread
from queue import Queue

def run_multideep(priorityQueue, objDetectorModel,alphaPoseModel):

    frame = priorityQueue.getitem()

    results = objDetectorModel.run(frame)
    alphapose_res = alphaPoseModel.run(priorityQueue)
    print(results)


