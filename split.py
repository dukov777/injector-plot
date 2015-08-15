#!/usr/bin/env python

import struct 
import argparse
from config import *


def find_packet_start(f):
    data = f.read(USB_LINE_SIZE*2)
    for i in range(0, USB_LINE_SIZE*2):
        timestamp = struct.unpack_from("<L", bytearray(data), i)
        timestamp2 = struct.unpack_from("<L", bytearray(data), i + INJECTORS)
        if timestamp == timestamp2:
            return i
    raise Exception("Packet is demaged")


def extract_injectors(f, channels):
    packet = f.read(USB_LINE_SIZE)[USB_LINE_HEADER_SIZE:]
    while len(packet) >= USB_LINE_SIZE - USB_LINE_HEADER_SIZE:
        for index, channel in enumerate(channels):
            channel.write(packet[index:len(packet):4])
        packet = f.read(USB_LINE_SIZE)[USB_LINE_HEADER_SIZE:]
    

def get_program_params():
    parser = argparse.ArgumentParser(description='Show Injetor Value.')
    
    parser.add_argument('filename',
                        help='file name')
    
    return parser.parse_args()


if __name__ == "__main__":

    args = get_program_params()
    
    f = open(args.filename)
    
    channels = []
    for channel in range(INJECTORS):
        channels.append(open(args.filename + '.' + str(channel), 'w'))
    
    start_index = find_packet_start(f)
    f.seek(0, start_index)
    
    extract_injectors(f, channels)

    for f in channels:
        f.close()
