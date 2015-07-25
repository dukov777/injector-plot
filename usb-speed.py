import usb1
import time
import sys
import struct 

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

BYTES = 10000000
BUFFER_SIZE = (BYTES / 64) * 64

f = open("measurements.msr", 'w')
before = time.time()
data = handle.bulkRead(1, BUFFER_SIZE, 50000)
f.write(data)   
print 'time for 1MByte is: ', time.time() - before
print 'Speed is: ', (BUFFER_SIZE / (time.time() - before))/1000, " [kByte/sec]"
f.close()

