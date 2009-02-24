"""
 " Probe Plotter v0.1
 " Plot the data retrieved from a probe.
 """

import drawer
import reader
import time
import serial
import gobject
import gtk

gobject.threads_init()

def min_max(data_list):
    first = data_list[0]
    last  = data_list[len(data_list) -1]
    minT = first[0]
    maxT = last[0]
    minP = first[1]
    maxP = first[1]
    for data in data_list:
        if maxP < data[1]: maxP = data[1]
        elif minP > data[1]: minP = data[1]
    return (minT, maxT, minP, maxP)

class ProbePlotter(drawer.Stage):
    def __init__(self, data):
        """
            @param data: The data list.
        """
        drawer.Stage.__init__(self)
        self.data = data
    
    def draw(self, ctx, width, height):
        length = len(self.data)
        if length < 2: return
        minT, maxT, minP, maxP = min_max(self.data)
        ts = float( width ) / ( maxT - minT )
        if minP == maxP:
            yoffset = height / 2
            ys = 0
        else:
            yoffset = 0
            ys = float( width ) / ( maxP - minP )
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(0, yoffset + ys * (self.data[0][1] - minP))
        for i in xrange(1, length):
            point = self.data[i]
            ctx.line_to((point[0] - minT) * ts, yoffset + (point[1] - minP) * ys)
        ctx.stroke()

class ProbeReader(reader.SerialLineReader):
    def __init__(self, conn, shared_list, data_len, max_points = 100):
        reader.SerialLineReader.__init__(self, conn)
        self.data_len = data_len
        self.shared_list = shared_list
        self.max_points = max_points
        self.output = None
    
    def set_output(self, fileName):
        self.output = open(fileName, "w")
    
    def on_data(self, data):
        instant = int( 1000 * time.time() )
        if len(data) != self.data_len:
            print "Data length error: ", data
        else:
            value = int( data.split(',')[2] )
            self.shared_list.append((instant, value))
            if len(self.shared_list) > self.max_points:
                self.shared_list.pop(0)
            if self.output:
                self.output.write(data + "\n")

data = []
cnx = serial.Serial("/dev/ttyUSB0", 19200, xonxoff=1)

rdr = ProbeReader(cnx, data, 18)
plt = ProbePlotter(data)

rdr.start()
plt.init_anim(33)

def on_quit(window, event):
    gtk.main_quit()
    rdr.running = False
    rdr.join()

wnd = gtk.Window()
wnd.add(plt)
wnd.show_all()
wnd.connect("delete-event", on_quit)

gtk.main()