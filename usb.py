#!/usr/bin/env python

import usb1
import time
import sys
import struct 
import argparse
from config import *


parser = argparse.ArgumentParser(description='Records Injetors.')

parser.add_argument('--samples', '-s', dest='samples', default=10, type=int,
          help='specifies how many bytes to be read per usb read operation '\
          '(default: 1 [kSample])')

parser.add_argument('--iter', '-i', dest='iter', default=1, type=int,
                   help='specifies how many usb reads to be done per file '\
                   '(default: 1). ')

parser.add_argument('--file', '-f', dest='filename', default='out.msr',
                   help='file name (default: out.msr)')

args = parser.parse_args()


context = usb1.USBContext()
handle = context.openByVendorIDAndProductID(
    VENDOR_ID, PRODUCT_ID,
    skip_on_error=True,
)
if handle is None:
    print "hui"
    # Device not present, or user is not allowed to access device.
handle.claimInterface(0)
print usb1.getVersion()

sequences = args.iter

BYTES = args.samples*1000
BUFFER_SIZE = (BYTES / 64) * 64
timeout = int(0.00002*BYTES)*1000



f = open(args.filename, 'w')
for _ in range(sequences):
    data = handle.bulkRead(1, BUFFER_SIZE, timeout)
    f.write(data)   

f.close()

