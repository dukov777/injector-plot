#!/usr/bin/env python

import struct 
import argparse
from config import *


class ICanvas:
    def plot(self, channel_name, samples):
        pass    
    
    def show(self):
        pass


class RemoteCanvas(ICanvas):
    traces = []
    def plot(self, channel_name, samples):
        self.traces.append(
            Scatter(
                    x=range(0, len(samples)),
                    y=samples
                ))
    
    def show(self):
        data = Data(self.traces)
    
        layout = Layout(
            yaxis=YAxis(
                range=[0, 255],
                autorange=False,
                rangemode = ['tozero' , 'nonnegative'],
            )
        )
        fig = Figure(data=data, layout=layout)
        unique_url = py.plot(fig, filename = 'basic-injector')


class LocalCanvas(ICanvas):
    labels = []
    def plot(self, channel_name, samples):
        plot(samples)
        self.labels.append(channel_name)
    
    def show(self):
        title(r'Injectors', fontsize=20)
        xlabel(r"time")
        legend(self.labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0.)
        show()    


def plot_injectors(channels, canvas):
    traces = []
    labels = []
    for channel_name, channel in channels:
        samples = channel.read()
        #scale down the samples array
        samples = samples[::args.scale]
        #convert from binary to normal form
        samples = map(lambda sample: struct.unpack('<B', sample)[0], samples)
        
        canvas.plot(channel_name, samples)
    canvas.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show Injetor Value.')

    parser.add_argument('--injector', dest='injector', default='all',
	                    choices=['0', '1', '2', '3', 'all'],
	                    help='Injector number [0..3, all] (default: all)')

    parser.add_argument('--file', dest='filename', default='out.msr',
	                    help='file name (default: out.msr)')

    parser.add_argument('--scale', dest='scale', default=1, type=int,
	                    help='how many samles to skip while ploting (default: 1)')

    parser.add_argument('--plot', dest='plot', default='local', type=str,
                        choices=['local', 'remote'],
	                    help='specify plot canvas (default: local)')

    args = parser.parse_args()

    channels = []
        
    if args.injector == "all":
        for channel in range(INJECTORS):
            channels.append(('injector {}'.format(channel),
                             open(args.filename + '.' + str(channel), 'r')))
    else:
        channels.append(('injector {}'.format(args.injector),
                         open(args.filename + '.' + args.injector, 'r')))

    if args.plot == 'local':
        from pylab import *
        canvas = LocalCanvas()
    else:
        import plotly.plotly as py
        from plotly.graph_objs import *
        canvas = RemoteCanvas()
    
    plot_injectors(channels, canvas)
