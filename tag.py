#!/usr/bin/env python

import os
import struct 
import argparse
from config import *
from array import array
import simplejson as serializer


def get_args():
    parser = argparse.ArgumentParser(description='Show Injetor Value.')

    parser.add_argument('filename', default='out.msr',
                        help='file name (default: out.msr)')
    parser.add_argument('--zeros', dest='nr_zeros', default=1, type=int,
                        help='how many zeros to delete')
    return parser.parse_args()


def clean_noise(sample):
    if sample < args.zero_level: 
        sample = 0

    return sample


def find_pulse(src):
    bytes_read = 0
    
    raw_byte = src.read(1)
    bytes_read += 1

    while raw_byte != "":
        byte = struct.unpack('<B', raw_byte)[0]
        byte = clean_noise(byte)
                
        if byte > 0:
            break

        raw_byte = src.read(1)
        bytes_read += 1

    pause_end = src.tell() - 1

    return pause_end


def find_pause(samples):
    number_of_zeros = 0
    last_pulse = 0
    for offset, sample in enumerate(samples):
        if sample == 0:
            number_of_zeros += 1
        else:
            last_pulse = offset
            number_of_zeros = 0
        
        if number_of_zeros > args.nr_zeros:
            pause_end = offset
            break
    else:
        raise IOError("Unable to find pause sequence!")
        
    return last_pulse, pause_end


def find_pulse(samples):
    number_of_zeros = 0
    for offset, sample in enumerate(samples):
        if sample != 0:
            break
    else:
        raise IOError("Unable to find pulse in the sequence!")
        
    return offset
    

TEMP_FILE_NAME = 'temp.msr'
pulse_wight = 100


if __name__ == "__main__":
    args = get_args()

    src_size = os.path.getsize(args.filename)
    
    src = open(args.filename, 'rb')
    dst = open(TEMP_FILE_NAME, 'wb+')

    samples = array('B')

    try:
        samples.fromfile(src, src_size)
    except EOFError as e:
        print e

    inject_pulses = []
    
    offset = 0    
    pulse_end, pause_end = find_pause(samples[offset:])
    pulse_end += offset 
    pause_end += offset
    
    try:
        while True:
            pulse_begining = find_pulse(samples[offset:])
            pulse_begining += offset
            
            offset = pulse_begining
            
            pulse_end, pause_end = find_pause(samples[offset:])
            pulse_end += offset 
            pause_end += offset
            
            offset = pause_end
            
            item = {'begin': pulse_begining, 
                    'end': pulse_end}
            inject_pulses.append(item)
    except IOError as e:
        pass
#         print e
    
    with open(args.filename+'.tags', 'w+') as f:
        for injection in inject_pulses:
            msg =  "pulse_begining {}, pulse_end {}".format(injection['begin'], 
                                                           injection['end'])
            print msg
            
    with open(args.filename+'.btags', 'w+') as f:
        serializer.dump(inject_pulses, f)

    dst.close()
    src.close()
    
#     os.rename(TEMP_FILE_NAME, args.filename)


