#!/usr/bin/env python

import usb1
import time
import sys
import struct 
import argparse


import array

INJECTORS = 4
USB_LINE_SIZE = 64
USB_LINE_HEADER_SIZE = 8

parser = argparse.ArgumentParser(description='Show Injetor Value.')

parser.add_argument('--file', dest='filename', default='out.msr',
                   help='file name (default: out.msr)')

args = parser.parse_args()


def find_packet_start(data):
    for i in range(0, USB_LINE_SIZE*2):
        timestamp = struct.unpack_from("<L", bytearray(data), i)
        timestamp2 = struct.unpack_from("<L", bytearray(data), i + INJECTORS)
        if timestamp == timestamp2:
            return data[i:]
    raise Exception("Packet is demaged")

if __name__ == "__main__":
    import os
    fsize = os.path.getsize(args.filename)
    print fsize    
    f = open(args.filename)
   
    prev = 0             
    for i in range(100000*1000):
        data = f.read(64)
        if len(data) == 64:
            timestamp = struct.unpack_from("<L", bytearray(data), 4)[0]
            if prev+1 != timestamp and i > 0:
                print "error in line {}. expected: {}, but received: {}".format(i, prev+1, timestamp)
            prev = timestamp
        elif len(data) == 0:
            print "exit"
            break
    f.close()
    
