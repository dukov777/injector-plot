#!/usr/bin/env python

import struct 
import argparse
from config import *
import simplejson as serializer
import os
import array



def get_args():
    parser = argparse.ArgumentParser(description='./show-tag.py latest.msr --injector 0')
    parser.add_argument('-i', '--injector', dest='injector', default='all',
                        choices=['0', '1', '2', '3', 'all'],
                        help='Injector number [0..3, all] (default: all)')
    parser.add_argument('filename', help='file name')
    parser.add_argument('-s', '--scale', dest='scale', default=1, type=int,
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
	
    def __init__(self):
        self.fig = pylab.figure(0,figsize=(8,7))
        self.ax = self.fig.add_subplot(111, 
                                  autoscale_on=False, 
                                  xlim=(0,850), 
                                  ylim=(-1,300))


    def set_xrange(self, xlim):
        pylab.xlim(xlim)


    def set_axline(self, x):
        l = pylab.plt.axvline(x=x)


    def plot(self, channel_name, samples, color):
        self.ax.plot(samples, color=color, label=channel_name, linewidth=2)
    
    
    def show(self):
#         title(r'Injectors', fontsize=20)
#         xlabel(r"time")
        _llegend = pylab.plt.legend(ncol=4, 
                                    loc='upper right', 
                                    shadow=True, 
                                    fontsize='small')
        _llegend.get_frame().set_facecolor('#00FFCC')
        pylab.show()
        
        
    def annotate(self, _str, _xy):
        self.ax.annotate(_str, 
                    xy=_xy,
                    xycoords='data',
                    xytext=(-10, -30),
                    rotation='vertical', 
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))


def plot_injectors(channels, canvas):
    COLORS = ['blue', 'red', 'black', 'green']
    for i, (channel_name, channel) in enumerate(channels):
        try:
            with open(channel+'.btags') as f:
                inject_pulses = serializer.load(f)
            
            src_size = os.path.getsize(channel)
            samples = array.array('B')

            with open(channel) as f:
                samples.fromfile(f, src_size)
        except IOError:
            continue
        
#         xlimit = 10 + sum(map(lambda item: 
#                               (item['end'] - item['begin'])/args.scale, 
#                               inject_pulses))
#         canvas.set_xrange(xlimit)
        
        plotter = []
        range_end = 0
        for index, inject in enumerate(inject_pulses):
            canvas.annotate('inj:' + str(index), (range_end, 0))
            
            injection_cycle = samples[inject['begin']:inject['end']:args.scale].tolist()
#             injection_cycle = map(lambda x: x + i*260, injection_cycle)
            plotter.extend(injection_cycle)

            range_end += (inject['end'] - inject['begin']) / args.scale
            range_end = len(plotter) - 1
            # trigget to channel 0
            if i == 0:
                canvas.set_axline(range_end)
            
        canvas.plot(channel_name, plotter, COLORS[i])
    canvas.show()


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
        import pylab
        canvas = LocalCanvas()
    else:
        import plotly.plotly as py
        from plotly.graph_objs import *
        canvas = RemoteCanvas()
    
    plot_injectors(channels, canvas)
