#!/usr/bin/env python

import usb1
import time
import sys
import struct 
import argparse
from pylab import *
from numpy  import *

import plotly.plotly as py
from plotly.graph_objs import *

INJECTORS = 4
USB_LINE_SIZE = 64
USB_LINE_HEADER_SIZE = 8



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
    

def plot_injectors_local(injectors):
    traces = []
    labels = []
    for id, injector in injectors:
    	plot(injector[0:len(injector):args.scale])
    	labels.append(id)
                    
    title(r'Injectors', fontsize=20)
    xlabel(r"time")
    legend(labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
    show()    

def plot_injectors_remote(channels):
    traces = []
    for channel in channels:
        data = channel.read()
        print "Input file size is: ", len(data), " bytes"
        print "Plotting ", len(data), " bytes"
        data = data[0:len(data):args.scale]
        traces.append(
            Scatter(
                    x=range(0, len(data)),
                    y=[struct.unpack('<B', x)[0] for x in data]
                ))
    
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
    parser = argparse.ArgumentParser(description='Show Injetor Value.')

    parser.add_argument('--injector', dest='injector', default='all', 
	                    choices=['0', '1', '2', '3', 'all'],
	                    help='Injector number [0..3, all] (default: all)')

    parser.add_argument('--file', dest='filename', default='out.msr',
	                    help='file name (default: out.msr)')

    parser.add_argument('--scale', dest='scale', default=1, type=int,
	                    help='how many samles to skip while ploting (default: 1000)')

    parser.add_argument('--plot', dest='plot', default='local', type=str,
                        choices=['local', 'remote'],
	                    help='specify plot canvas (default: local)')

    args = parser.parse_args()

    f = open(args.filename)
    data = f.read()
    f.close()

    data = find_packet_start(data)
    injectors = extract_injectors(data)

    if args.injector != 'all':
        injector = ('injector {}'.format(args.injector), 
                    injectors[int(args.injector)])
        injectors = []
        injectors.append(injector)
    else:
        temp = []
        for i, injector in enumerate(injectors):
            temp.append(('injector {}'.format(i), injector))
        injectors = temp      
    
    if args.plot == 'local':
        plot_injectors_local(injectors)
    else:
        channels = []
        
        if args.injector == "all":
            for channel in range(INJECTORS):
                channels.append(open(args.filename + '.' + str(channel), 'r'))
        else:
            channels.append(open(args.filename + '.' + args.injector, 'r'))
        plot_injectors_remote(channels)

