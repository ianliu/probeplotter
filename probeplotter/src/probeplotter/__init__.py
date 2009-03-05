
"""

Probe Plotter v0.1
Plot the data retrieved from a probe.

"""

import serial
import gtk, gobject
from gtk import glade
import drawer, reader
from serial.serialutil import SerialException

gobject.threads_init()



class MainWindow(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		
		# These variables are to be chosen by the user
		self.reader         = None
		self.drawer         = None
		self.info           = None # Keep this for initialization purposes
		self.data           = []
		
		self.__layout()
		self.__connect_signals()
	
	def connect_probe(self):
		info = self.info
		if info['id'] == reader.FAKE_READER:
			self.reader = reader.FakeReader(self.data, info['interval'])
		elif info['id'] == reader.SPY_READER:
			conn = serial.Serial(info['port'], 19200, xonxoff=1)
			self.reader = reader.ProbeReader(conn, self.data, info['data_size'])
		
		self.drawer = drawer.ProbePlotter(self.data)
		self.reader.start()
		self.drawer.init_anim(66)
		self.container.add(self.drawer)
		self.drawer.show()
	
	def disconnect_probe(self):
		child = self.container.get_child()
		if child:
			self.container.remove(child)
			child.destroy()
		self.reader.running = False
		self.reader.join()
		self.data = []
	
	def __layout(self):
		# Widget creation
		vbox                = gtk.VBox()
		tool                = gtk.Toolbar()
		yes_radio           = gtk.RadioToolButton(None, gtk.STOCK_YES)
		no_radio            = gtk.RadioToolButton(yes_radio, gtk.STOCK_NO)
		self.statusbar      = gtk.Statusbar()
		self.status_context = self.statusbar.get_context_id('MainWindow')
		self.container      = gtk.Viewport()
		self.config_dialog  = drawer.ConfigDialog('Configuration Dialog', self)
		self.connect_btn    = gtk.ToggleToolButton(gtk.STOCK_CONNECT)
		self.configure_btn  = gtk.ToolButton(gtk.STOCK_PREFERENCES)
		
		# Packing
		tool.insert(self.connect_btn, -1)
		tool.insert(gtk.SeparatorToolItem(), -1)
		tool.insert(drawer.ToolLabel("  Capture?  "), -1)
		tool.insert(yes_radio, -1)
		tool.insert(no_radio, -1)
		tool.insert(gtk.SeparatorToolItem(), -1)
		tool.insert(self.configure_btn, -1)
		vbox.pack_start(tool, False)
		vbox.add(self.container)
		vbox.pack_start(self.statusbar, False)
		self.add(vbox)
		self.config_dialog.add_page(drawer.FakeConfig())
		self.config_dialog.add_page(drawer.SpyConfig())
		
		# Styling
		self.connect_btn.set_use_underline(True)
		tool.set_style(gtk.TOOLBAR_BOTH)
		self.connect_btn.set_tooltip_markup("Connect")
		self.container.set_shadow_type(gtk.SHADOW_NONE)
		self.set_default_size(550, 400)
		self.show_all()
	
	def __connect_signals(self):
		self.connect_btn.connect('toggled', self.__connect_toggled)
		self.configure_btn.connect('clicked', self.__configure_clicked)
		self.connect('destroy', self.__quit)
	
	
	# Signals
	
	def __connect_toggled(self, btn):
		if btn.get_active():
			btn.set_stock_id(gtk.STOCK_DISCONNECT)
			self.connect_btn.set_tooltip_markup("Disconnect")
			if self.info:
				self.connect_probe()
			else:
				self.__configure_clicked(self.config_dialog)
		else:
			btn.set_stock_id(gtk.STOCK_CONNECT)
			self.connect_btn.set_tooltip_markup("Connect")
			self.disconnect_probe()

	def __configure_clicked(self, btn):
		response = self.config_dialog.run()
		if self.connect_btn.get_active() and response == gtk.RESPONSE_APPLY:
			self.info = self.config_dialog.get_config()
			self.connect_probe()
		self.config_dialog.hide()
	
	def __quit(self, window):
		gtk.main_quit()



if __name__ == "__main__":
	MainWindow()
	gtk.main()
