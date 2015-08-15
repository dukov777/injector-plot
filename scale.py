#!/usr/bin/env python

import os
import struct 
import argparse
from config import *
from array import array
from math import floor


TEMP_FILE_NAME = 'temp.msr'


def get_args():
    parser = argparse.ArgumentParser(description='Show Injetor Value.')
    parser.add_argument('filename',
                        help='file name (default: out.msr)')
    parser.add_argument('--scale', dest='scale', default=1, type=float,
                        help='')
    return parser.parse_args()
            

def scale(input, output):
    for i in xrange(len(input)):
        tmp = int(floor(args.scale * input[i]))
        if tmp > 255:
            tmp = 255

        input[i] = tmp 


if __name__ == "__main__":
    args = get_args()
    
    src = open(args.filename, 'rb')
    src_size = os.path.getsize(args.filename)
    
    dst = open(TEMP_FILE_NAME, 'wb+')
    
    sample = array('B')
    try:
        sample.fromfile(src, src_size)
    except EOFError as e:
        print e
    
    prev = sample[:]
    # clean peaks of one sample
    scale(sample, sample)
    
#     if cmp(prev, sample): print 'error'
    
#     print sample[:100]
    try:
        sample.tofile(dst)
#         dst.write(sample[:100])
    except EOFError as e:
        print e

    dst.close()
    src.close()
    
    os.rename(TEMP_FILE_NAME, args.filename)
    