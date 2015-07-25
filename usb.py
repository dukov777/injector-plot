import usb1
import time
import sys
import struct 
import argparse

parser = argparse.ArgumentParser(description='Records Injetors.')

parser.add_argument('--samples', dest='samples', default=1,
                   help='mega samples per usb read operation (default: 1 [MegaSample])')

parser.add_argument('--iter', dest='iter', default=1,
                   help='usb reads per file (default: 1). ')

parser.add_argument('--file', dest='filename', default='out.msr',
                   help='file name (default: out.msr)')

args = parser.parse_args()

VENDOR_ID = 0x04d8
PRODUCT_ID = 0x0052

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

sequences = int(args.iter)

BYTES = int(args.samples)*1000*1000
BUFFER_SIZE = (BYTES / 64) * 64
timeout = int(0.00002*BYTES)*1000



f = open(args.filename, 'w')
for _ in range(sequences):
    data = handle.bulkRead(1, BUFFER_SIZE, timeout)
    f.write(data)   

f.close()

