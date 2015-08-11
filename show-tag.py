#!/usr/bin/env python

import struct 
import argparse
from config import *
import simplejson as serializer


def get_args():
    parser = argparse.ArgumentParser(description='./show-tag.py latest.msr --injector 0')
    parser.add_argument('--injector', dest='injector', default='all',
                        choices=['0', '1', '2', '3', 'all'],
                        help='Injector number [0..3, all] (default: all)')
    parser.add_argument('filename', help='file name')
    parser.add_argument('--scale', dest='scale', default=1, type=int,
                        help='how many samles to skip while ploting (default: 1)')
    parser.add_argument('--plot', dest='plot', default='local', type=str,
                        choices=['local', 'remote'],
                        help='specify plot canvas (default: local)')
    return parser.parse_args()



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
    colours = ['blue', 'red', 'black', 'green']
    for i, (channel_name, channel) in enumerate(channels):
        with open(channel+'.btags') as f:
            inject_pulses = serializer.load(f)
        
        import os
        from array import array

        src_size = os.path.getsize(channel)
        samples = array('B')        
        with open(channel) as f:
            samples.fromfile(f, src_size)
        
        fig = figure(1,figsize=(8,5))
        ax = fig.add_subplot(111, autoscale_on=False, xlim=(0,2000), ylim=(-1,300))

        plotter = []
        for index, inject in enumerate(inject_pulses):
            #scale down the samples array
            print inject['begin'], inject['end']
            ax.annotate('injection ' + str(index), 
                        xy=(len(plotter)-1, 0),
                        xycoords='data',
                        xytext=(-30, -30), 
                        textcoords='offset points',
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3")
                        )

            plotter.extend(samples[inject['begin']:inject['end']].tolist())
            l = plt.axvline(x=len(plotter))
            
        plot(plotter, color=colours[i+1], label=channel_name, linewidth=2)
    _llegend = plt.legend(ncol=4, loc='upper right', shadow=True, fontsize='small')
    _llegend.get_frame().set_facecolor('#00FFCC')
    
    show()


if __name__ == "__main__":
    args = get_args()

    channels = []
        
    if args.injector == "all":
        for channel in range(INJECTORS):
            channels.append(('injector {}'.format(channel),
                             args.filename + '.' + str(channel)))
    else:
        name = args.filename + '.' + args.injector
        channels.append(('injector {}'.format(args.injector), name))

    if args.plot == 'local':
        from pylab import *
        canvas = LocalCanvas()
    else:
        import plotly.plotly as py
        from plotly.graph_objs import *
        canvas = RemoteCanvas()
    
    plot_injectors(channels, canvas)