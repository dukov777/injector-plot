import usb1
import time
import sys
import struct 
import argparse

import plotly.plotly as py
from plotly.graph_objs import *

INJECTORS = 4
USB_LINE_SIZE = 64
USB_LINE_HEADER_SIZE = 8

parser = argparse.ArgumentParser(description='Show Injetor Value.')

parser.add_argument('--injector', dest='injector', default='all',
                   help='Injector number (default: all)')

parser.add_argument('--file', dest='filename', default='out.msr',
                   help='file name (default: out.msr)')

parser.add_argument('--scale', dest='scale', default=1000,
                   help='how many samles to skip while ploting (default: 1000)')

args = parser.parse_args()


def find_packet_start(data):
    for i in range(0, USB_LINE_SIZE*2):
        timestamp = struct.unpack_from("<L", bytearray(data), i)
        timestamp2 = struct.unpack_from("<L", bytearray(data), i + INJECTORS)
        if timestamp == timestamp2:
            return data[i:]
    raise Exception("Packet is demaged")

def extract_injectors(data): 
    injectors = []
    for inj_nr in range(INJECTORS):
        injector = []
        for i in range(0, len(data), USB_LINE_SIZE):
            pack = data[i+USB_LINE_HEADER_SIZE:i+USB_LINE_SIZE]
            result = map(lambda x: struct.unpack("<B", bytearray(x))[0], pack)
            injector += result[inj_nr:len(result):INJECTORS]
        injectors.append(injector)
    return injectors
    
def plot_injectors(injectors):
    traces = []
    for injector in injectors:
        injector = injector[0:len(injector):int(args.scale)]
        traces.append(
            Scatter(
                    x=range(0, len(injector)),
                    y=injector
                ))
                
    #print injectors

    data = Data(traces)

    layout = Layout(
        yaxis=YAxis(
            range=[0, 255],
            autorange=False,
            rangemode = ['tozero' , 'nonnegative'],
        )
    )
    fig = Figure(data=data, layout=layout)
    unique_url = py.plot(fig, filename = 'basic-injector')

    
if __name__ == "__main__":
    f = open(args.filename)
    data = f.read()
    f.close()

    data = find_packet_start(data)
    injectors = extract_injectors(data)

    if args.injector != 'all':
        injector = injectors[int(args.injector)]
        injectors = []
        injectors.append(injector)

    plot_injectors(injectors)

