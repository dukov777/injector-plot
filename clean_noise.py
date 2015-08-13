#!/usr/bin/env python

import os
import struct 
import argparse
from config import *
from array import array


TEMP_FILE_NAME = 'temp.msr'


def get_args():
    parser = argparse.ArgumentParser(description='Show Injetor Value.')
    parser.add_argument('filename',
                        help='file name (default: out.msr)')
    parser.add_argument('--zero-level', dest='zero_level', default=10, type=int,
                        help='')
    return parser.parse_args()
            

def clean_low_level_noise(sample):
    if sample < args.zero_level: 
        sample = 0

    return sample


def lowpass_filter(input, output):
    input[0] = clean_low_level_noise(input[0]) 

    for i in xrange(1, len(input)):
        input[i] = clean_low_level_noise(input[i]) 
        
        #clean peaks
        if input[i] > 0 and input[i-1] == 0 and input[i+1] == 0:
            input[i] = 0 


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
    lowpass_filter(sample, sample)
    
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
    