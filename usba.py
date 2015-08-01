#!/usr/bin/env python

import usb1
import os
import time
import sys
import struct 
import argparse
from config import *
import pyaio


def file_write_end(rt, er):
    if rt == 0:
        print "Got error: %d" % errno
        sys.exit()
    else:
         print "Wrote %d bytes" % rt
        

inc = 0
prop = ['/', '+', '\\']
def propeller(end = ''):
    if end == 'end':
        sys.stdout.write("\b")
        sys.stdout.flush()
    else:
        global inc
        inc += 1
        if inc == len(prop):
            inc = 0
        sys.stdout.write("\b")
        sys.stdout.write(prop[inc])
        sys.stdout.flush()

    
    
def received_usb_data(transfer):
    if transfer.getStatus() != usb1.TRANSFER_COMPLETED:
        print "Transfer did not complete successfully, there is no data to read.\
        This example does not resubmit transfers on errors. You may want\
        to resubmit in some cases (timeout, ...)."
        return
    
    print "transfer.getActualLength()  ", transfer.getActualLength()
    data = transfer.getBuffer()[:transfer.getActualLength()]
    
    global reads_per_file

    reads_per_file -= 1
    if reads_per_file > 0:
        transfer.submit()
    ret = pyaio.aio_write(out_file, data, 0, file_write_end)
    assert ret == 0

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Records Injetors.')
    
    parser.add_argument('--samples', '-s', dest='samples', default=10, type=int,
              help='specifies how many bytes to be read per usb read operation. '\
              '(default: 10 [64 kBytes])')
    
    parser.add_argument('--iter', '-i', dest='iter', default=1, type=int,
                       help='specifies how many usb reads to be done per file '\
                       '(default: 1). ')
    
    parser.add_argument('--file', '-f', dest='filename', default='out.msr',
                       help='file name (default: out.msr)')
    
    args = parser.parse_args()
    
    reads_per_file = args.iter
    
    TRANSFER_COUNT = 1
    BYTES = args.samples*1000
    BUFFER_SIZE = BYTES * 64

    context = usb1.USBContext()
    handle = context.openByVendorIDAndProductID(
        VENDOR_ID, PRODUCT_ID,
        skip_on_error=True,
    )
    
    if handle is None:
        print "Device not present, or user is not allowed to access device."
        sys.exit()
        
    handle.claimInterface(0)
    
    out_file = os.open(args.filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_APPEND )
    # Build a list of transfer objects and submit them to prime the pump.
    transfer_list = []
    for _ in xrange(TRANSFER_COUNT):
        transfer = handle.getTransfer()
        transfer.setBulk(
            usb1.ENDPOINT_IN | 0x01,
            BUFFER_SIZE,
            callback=received_usb_data,
        )
        transfer.submit()
        transfer_list.append(transfer)
        
    # Loop as long as there is at least one submitted transfer.
    while any(x.isSubmitted() for x in transfer_list):
        try:
            context.handleEvents()
            propeller()
        except usb1.USBErrorInterrupted:
            pass
    propeller('end')
    print "end"