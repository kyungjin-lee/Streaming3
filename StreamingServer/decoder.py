import numpy as np
#import libh264decoder


def run_decode(decoder, data_in):
    framedatas = decoder.decode(data_in)
    for framedata in framedatas:
        (frame, w, h, ls) = framedata
        print ("$$$$$$$$$  w, h, ls: ",  w, h, ls)
       	if frame is not None:
            frame = np.fromstring(frame, dtype=np.ubyte, count = len(frame), sep ='')
            frame = frame.reshape((h,int(ls/3), 3))
            frame = frame[:,:w,:]
            return frame

     
