import sys, threading, socket
from rtp import RTP
import struct
import cv2

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
   
    
    def __init__(self, clientInfo):
        self.clientInfo = clientInfo
        self.rtp_parser = RTP()
        self.data = b''
        self.data_len = 0
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
        #Get the request type
#        data_str = data.decode()

#        if data_str[0] is not '$':
#            request = data_str.split('\n')
#            line1 = request[0].split(' ')
#            requestType = line1[0]
#            #Get the media file name
#            #filename = line1[1]
#            #Get the RTSP sequence number
#            seq = request[1].split(' ')
#    
#            rtspVersion = line1[1]
#            cseq = (request[1].split(' '))[1]
#            if requestType == self.OPTIONS:
#                self.replyRtsp(self.OK_200, cseq)
#    
#            elif requestType == self.ANNOUNCE:
#                self.replyRtsp(self.OK_200, cseq)
#    
#            elif requestType == self.SETUP:
#                self.replyRtsp(self.OK_200, cseq)
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
