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
	
	The Stage class offers a loop for animating.
	It should be extended and the draw method
	overridden.
	
	"""
	
	def __init__(self, clear_color = (1, 1, 1)):
		
		"""
		Creates a new plot area.
		@param clear_color: The background color
		"""
		gtk.DrawingArea.__init__(self)
		self.time = 0
		self._anim = False
		self.clear_color = clear_color
		self.connect("expose-event", self._on_expose_event)
		
	
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
		if length < 2: return
		minT, maxT, minP, maxP = min_max(self.data)
		if minT == maxT: return
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



class ConfigDialog(gtk.Dialog):
	def __init__(self, title, parent):
		gtk.Dialog.__init__(self, title, parent,
						gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						gtk.STOCK_OK, gtk.RESPONSE_APPLY))
		
		self.container = gtk.Viewport()
		self.container.set_shadow_type(gtk.SHADOW_NONE)
		self.current = None
		self.pages = []
		self.combo = gtk.combo_box_new_text()
		
		box = gtk.HButtonBox()
		box.add(self.combo)
		
		self.vbox.pack_start(box, False)
		self.vbox.add(self.container)
		self.vbox.show_all()
		self.vbox.set_spacing(10)
		self.combo.connect('changed', self.on_changed)
		self.set_has_separator(False)
	
	def on_changed(self, cb):
		i = cb.get_active()
		child = self.container.get_child()
		if child: self.container.remove(child)
		self.container.add(self.pages[i])
		self.pages[i].show_all()
		self.current = self.pages[i]
	
	def add_page(self, page):
		self.pages.append(page)
		self.combo.append_text(page.name)
		if not self.current:
			self.combo.set_active(0)
			self.current = page
	
	def get_config(self):
		return self.current.get_config()


class FakeConfig(gtk.Frame):
	def __init__(self):
		gtk.Frame.__init__(self, 'Fake reader configuration')
		self.set_name('Fake reader')
		self.set_shadow_type(gtk.SHADOW_OUT)
		
		box   = gtk.HButtonBox()
		label = gtk.Label('Interval (in seconds)')
		adj   = gtk.Adjustment(1, 0.1, 1, 0.1)
		spin  = gtk.SpinButton(adj, 0, 2)
		spin.set_numeric(True)
		box.add(label)
		box.add(spin)
		self.add(box)
		self.spin = spin
	
	def get_config(self):
		return {'interval': self.spin.get_value()}


class SpyConfig(gtk.Frame):
	def __init__(self):
		gtk.Frame.__init__(self, 'Spy configuration')
		self.set_name("Spy reader")
		vbox = gtk.VBox()
		size = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		
		box = gtk.HBox()
		label = gtk.Label("Serial port:")
		combo = gtk.combo_box_entry_new_text()
		size.add_widget(combo)
		box.add(label)
		box.pack_start(combo, False, False)
		vbox.add(box)

		combo.append_text("COM1")
		combo.append_text("COM2")
		combo.append_text("COM3")
		combo.append_text("COM4")
		combo.set_active(0)
		self.combo = combo

		box = gtk.HBox()
		label = gtk.Label("Data size:")
		adjust = gtk.Adjustment(18, 0, 50, 1)
		spin = gtk.SpinButton(adjust)
		size.add_widget(spin)
		box.add(label)
		box.pack_start(spin, False, False)
		vbox.add(box)
		self.spin = spin

		self.add(vbox)
	
	def get_config(self):
		return {
			'port': self.combo.get_active(),
			'data_size': self.spin.get_value()
		}
		
		



