from rfc3984 import RFC3984
from decoder import run_decode
import libh264decoder
import bitstring

PT_H264 = 96

class RTP(object):
    
    def __init__(self):
        self._first_pkt = False
        self._rtp_sn = -1
        self._payload_type = None


        self._codec_depay = { PT_H264: RFC3984}
        self._rfc3984 = RFC3984()

        self._first_fua = False
        self._decoder = libh264decoder.H264Decoder()

    def parse_csrc(self, pkt, cc, lc):
        bt = bitstring.BitArray(bytes=pkt)
        cids = []
        bc = 8*lc
        for i in range(cc):
            cids.append(bt[bc:bc+32].uint)
            bc += 32
            lc +=4
        print ("csrc identifiers:", cids)

        return lc

    def parse_ext_hdr(self, pkt, lc):
        bt = bitstring.BitArray(bytes=pkt)
        bc = 8*lc
        hid = bt[bc:bc+16].uint
        bc += 16
        lc +=2

        hlen = bt[bc:bc+16].uint
        bc += 16
        lc += 2

        print ("ext. header id, header len", hid, hlen)

        hst = bt[bc:bc+32*hlen]
        bc += 32*hlen
        lc += 4*hlen

        return lc

    def parse_header(self, pkt):
        bt = bitstring.BitArray(bytes=pkt)
        if self._first_pkt == False:
            self._first_pkt = True

        v2 = bt[0:2]
        version = bt[0:2].uint # version
        p = bt[3] # P
        x = bt[4] # X
        cc = bt[4:8].uint #cc
        m = bt[9] # M
        pt = bt[9:16].uint #PT
        sn = bt[16:32].uint # sequence number
        timestamp = bt[32:64].uint # timestamp
        ssrc = bt[64:96].uint # ssrc identifier

        if pt in self._codec_depay:
            codec_depay = self._codec_depay[pt]()

        print ("version p, x, cc, m, pt ", version, p, x, cc, m, pt)
        print ("sequence number, timestamp ", sn, timestamp)
        self._rtp_sn = sn

        lc = 12 #read twelve bytes
        bc = 12*8 #read 12*8 bits

        lc = self.parse_csrc(pkt, cc, lc)
      
        if (x):
            lc = self.parse_ext_hdr(pkt[lc:], bc, lc)
            bc = 8*lc

        frame = self._rfc3984.parse_frame(pkt[lc:])

        if frame != None:
            decoded_frame = run_decode(self._decoder, frame)
            return decoded_frame

    def recv_pkt(self, pkt):
        print("recv pkt")
        decoded_frame = self.parse_header(pkt)
        return decoded_frame

