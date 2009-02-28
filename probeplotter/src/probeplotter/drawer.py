"""

Provides classes to animate on a gtk.DrawingArea.

"""

import gtk
import gobject

from gtk import glade

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

class Stage(gtk.DrawingArea):
	
	"""
	
	The Stage.
	
	"""
	
	def __init__(self, clear_color = (1, 1, 1)):
		
		"""
		Creates a new plot area.
		@param clear_color: The background color
		"""
		gtk.DrawingArea.__init__(self)
		self.connect("expose-event", self._on_expose_event)
		self.clear_color = clear_color
		self.time = 0
		
		# Private
		self._anim = False
	
	def draw(self, ctx, width, height):
		
		"""
		Override this method to draw on the Stage.
		"""
		pass
	
	def on_anim(self, t):
		
		"""
		Override this method. Fired whenever an animation frame is reached.
		"""
		pass
	
	def init_anim(self, interval):
		
		"""
		Initiates the animation with given interval between frames.
		"""
		self.time = 0
		self._anim = True
		gobject.timeout_add(interval, self._animate)
	
	def stop_anim(self):
		
		"""
		Stops the animation.
		"""
		self._anim = False
	
	# Private methods
	def _on_expose_event(self, widget, event):
		x, y, width, height = self.get_allocation()
		ctx = self.window.cairo_create()
		ctx.set_source_rgb( *self.clear_color )
		ctx.rectangle(0, 0, width, height)
		ctx.fill()
		self.draw(ctx, width, height)
	
	def _animate(self):
		self.on_anim( self.time )
		self.time += 1
		self.queue_draw()
		return self._anim

class ProbePlotter(Stage):
	
	"""
	Default Plotter.
	"""
	
	def __init__(self, data):
		
		"""
		@param data: The data list.
		"""
		Stage.__init__(self)
		self.data = data
	
	# Override
	def draw(self, ctx, width, height):
		
		"""
		Draws the graphic.
		"""
		length = len(self.data)
		minT, maxT, minP, maxP = min_max(self.data)
		if length < 2 or minT == maxT: return
		ts = float( width ) / ( maxT - minT )
		if minP == maxP:
			yoffset = height / 2
			ys = 0
		else:
			yoffset = 0
			ys = float( height ) / ( maxP - minP )
		ctx.set_source_rgb(0, 0, 0)
		ctx.move_to(0, yoffset + ys * (self.data[0][1] - minP))
		for i in xrange(1, length):
			point = self.data[i]
			ctx.line_to((point[0] - minT) * ts, yoffset + (point[1] - minP) * ys)
		ctx.stroke()

