import socket
import cv2
from optparse import OptionParser
import sys
from rtp import RTP
import datetime
from Server import Server

MAX_RTP_SEQ_NUM = 65535

def main():

    server_addr = ('', 554)
    rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rtspSocket.bind(server_addr)
    print("RTSP listening client request...")
    rtspSocket.listen(5)

    while True:
        clientInfo = {}
        clientInfo['rtspSocket'] = rtspSocket.accept()
        Server(clientInfo).run()
#       clientSocket, addr = rtspSocket.accept()
#       data = clientSocket.recv(2048)
#       if not data:
#           print("client does not exist")
#           break
#       decoded_frame = rtp_parser.recv_pkt(data)
       
#    with conn:
#        while True:
#            data = conn.recv(MAX_RTP_PKT_LEN)
#    
#            if not data:
#                print ("client does not exist")
#                break
#            decoded_frame = rtp_parser.recv_pkt(data)
#            if decoded_frame is not None:
#                print ("start: ", datetime.datetime.now())
#                img = cv2.cvtColor(decoded_frame, cv2.COLOR_RGB2BGR)
#                cv2.imshow("preview", img)
#                key = cv2.waitKey(1)
#                if key&0xFF == ord('q'):
#                    break
#        s.close()
if __name__ == '__main__':
    main()
