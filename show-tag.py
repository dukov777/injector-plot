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
                                  xlim=(0,150), 
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
        pylab.show(block=False)
    
    
    def close(self):
        pylab.close('all')
        
        
    def annotate(self, _str, _xy):
        self.ax.annotate(_str, 
                    xy=_xy,
                    xycoords='data',
                    xytext=(-10, -30),
                    rotation='vertical', 
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))


def __make_frames(inject_pulses, samples):
    frames = []
    for index, inject in enumerate(inject_pulses):
        injection_cycle = samples[inject['begin']:inject['end']:args.scale].tolist()
        inj = {'data': injection_cycle,
               'range': (inject['begin'], inject['end']),
               'name': 'inj:' + str(index)}
        frames.append(inj)
    return frames


def __draw_frames(injector_id, channel_name, frames):
    COLORS = ['blue', 'red', 'black', 'green']
    plotter = []
    range_end = 0
    for index, inject in enumerate(frames):
        middle = range_end + len(inject['data'])/2
        canvas.annotate(inject['name'], (middle, 0))
        range_end += len(inject['data'])
        
        inj = inject['data']
#         inj = map(lambda x: x + injector_id*260, inj)
#         pylab.ylim(-1, (max(inj))+10)
        plotter.extend(inj)

#         range_end += (inject['range'][1] - inject['range'][0]) / args.scale
#         range_end -= 1
        # trigget to channel 0
        if injector_id == 0:
            canvas.set_axline(range_end)
        
    canvas.plot(channel_name, plotter, COLORS[injector_id])


def __align_frames(channels, canvas):
    cylinders = []
    for injector_id, (_, channel) in enumerate(channels):
        try:
            inject_pulses, samples = __read_samples(channel)
        except IOError:
            continue
        
        frames = __make_frames(inject_pulses, samples)
        cylinders.append(frames)
    
    def __get_len(frame):
        if frame != None:
            return frame['range'][1] - frame['range'][0]
        else:
            return 0
    def find_max(i0, i1, i2, i3):
        __max =  max(__get_len(i0), __get_len(i1), __get_len(i2), __get_len(i3))
        # make max even
        __max = ((__max + 1) / 2) * 2
        return __max
    __max_len = map(find_max, *[x for x in cylinders])
    
    def __extend_plot(data, __max):
        if __max % 2 != 0:
            raise "max should be in power of 2"
        # make 'data' even
        if len(data) % 2 != 0:
            data.extend([0])
             
        middle = __max / 2
        arr = [0 for _ in range(__max)]
        # insert 'data' in the middle of arr
        arr[middle - len(data)/2 : middle + len(data)/2] = data
        return arr

    for cylinder in cylinders:
        for index, frame in enumerate(cylinder):
            if __get_len(frame) < __max_len[index]:
                frame['data'] = __extend_plot(frame['data'], __max_len[index])

    for injector_id, (channel_name, channel) in enumerate(channels):
        frames = cylinders[injector_id]
        __draw_frames(injector_id, channel_name, frames)       
    
    canvas.show()


def __read_samples(channel):
    with open(channel+'.btags') as f:
        inject_pulses = serializer.load(f)
    
    src_size = os.path.getsize(channel)
    samples = array.array('B')

    with open(channel) as f:
        samples.fromfile(f, src_size)

    return inject_pulses, samples

    
def plot_injectors(channels, canvas):
    for injector_id, (channel_name, channel) in enumerate(channels):
        try:
            inject_pulses, samples = __read_samples(channel)
        except IOError:
            continue
        
        frames = __make_frames(inject_pulses, samples)
        __draw_frames(injector_id, channel_name, frames)       
    canvas.show()

step = 150
s_begin = 0
s_end = s_begin + step

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
    
    __align_frames(channels, canvas)
    
    import Tkinter as tk
    
    master = tk.Tk()
    
    def __increment():
        global s_end
        global s_begin
        s_begin += step
        s_end += step
        canvas.set_xrange((s_begin,s_end))
        canvas.show()

    def __decrement():
        global s_end
        global s_begin
        s_begin -= step
        s_end -= step
        canvas.set_xrange((s_begin,s_end))
        canvas.show()

    def __close():
        master.quit()
        canvas.close()
        
    master.bind('<KeyPress-Left>', lambda _: __decrement())
    master.bind('<KeyPress-Right>', lambda _: __increment())
    master.bind('<KeyPress-q>', lambda _: __close())

    frame = tk.Frame(master)
    frame.pack()
    b = tk.Button(frame, text="next", underline=0, command=__increment)
    b.pack(side=tk.LEFT)

    b2 = tk.Button(frame, text="Quit", command=__close)
    b2.pack(side=tk.LEFT)
    
    master.mainloop()
    master.destroy()
    