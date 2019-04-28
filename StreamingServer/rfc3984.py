import bitstring
import struct

TYPE_SINGLE_NALU_01 = 1
TYPE_SINGLE_NALU_23 = 23
TYPE_STAPA = 24
TYPE_NALU_FUA = 28
START_BYTES = "\x00\x00\x00\x01"
PT_H264 = 96

class RFC3984(object):
    def parse_frame(self, pay):
        frame = None
        bt = bitstring.BitArray(bytes=pay)
        bc = 0
        lc = 0
        #NAL unit indicator
        fb = bt[bc] # "F"
        nri = bt[bc+1:bc+3].uint # "NRI"
        nlu0 = bt[bc:bc+3] # "3 NAL UNIT BITS" ( "F" | "NRI"
        typ = bt[bc+3:bc+8].uint # "TYPE"

        print ("F, NRI, Type : ", fb, nri, typ)
        
        if (typ >= TYPE_SINGLE_NALU_01) and (typ <= TYPE_SINGLE_NALU_23):
            print (">>> Single NALU", typ)
            frame = START_BYTES.encode() + pay[lc:]
        elif typ == TYPE_STAPA:
            spslen = struct.unpack('>H',pay[lc+1:lc+3])[0]
            ppslen = struct.unpack('>H',pay[lc+3+spslen:lc+5+spslen])[0]
            sps = pay[lc+3:lc+3+spslen]
            pps = pay[lc+5+spslen:lc+5+spslen+ppslen]
            print("sps: ", sps, " pps: ", pps)
            frame = START_BYTES.encode() + sps + START_BYTES.encode() + pps
            

        bc += 8
        lc += 1

        # NALU Header
        start = bt[bc] # start bit
        end = bt[bc+1] # end bit
        nlu1 = bt[bc+3:bc+8] # 5 nal unit bits

        nlu = nlu0 + nlu1
        head = START_BYTES.encode() + nlu.bytes
        bc += 8
        lc += 1

        if typ == TYPE_NALU_FUA:
            if(start):
                print (">>> First FUA", nlu1.uint)
                frame = head+pay[lc:]
            else:
                print (">>> FUA", nlu1.uint)
                frame = pay[lc:]
        return frame



