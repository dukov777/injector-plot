#!/usr/bin/env python

import argparse
from config import *
from array import array
import os

TEMP_FILE_NAME = 'temp.msr'


def get_program_params():
    parser = argparse.ArgumentParser(description='Show Injetor Value.')
    
    parser.add_argument('filename', help='file name')
    parser.add_argument('--extract', dest='extract', type=str,
                        help='file name to store the cut range')
    parser.add_argument('-b', dest='begin', type=int, default=0,
                        help='cut range begin')
    parser.add_argument('-e', dest='end', type=int, default=-1,
                        help='cut range end')
    return parser.parse_args()


if __name__ == "__main__":

    args = get_program_params()
    if args.end < 0:
        args.end = os.path.getsize(args.filename)
    if args.begin < 0:
        print "wrong range, begin is negative"
        exit()
    if args.begin > args.end:
        print "wrong range, begin is bigger than end"
        exit()
    if args.end > os.path.getsize(args.filename):
        print "wrong range, end is bigger than file elements"
        exit()
        
    src = open(args.filename, 'rb')
    dst = open(TEMP_FILE_NAME, 'wb+')
    
    dst.write(src.read(args.begin))
    cutted_range = src.read(args.end - args.begin)
    dst.write(src.read())

    if args.extract:
        with open(args.extract, 'wb+') as extract:
            extract.write(cutted_range)

    dst.close()
    src.close()
    
    os.rename(TEMP_FILE_NAME, args.filename)
