
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
		# TODO: Implement a parser and make reader receive it
		self.parser         = None
		self.reader         = None
		self.drawer         = None
		
		self.__layout()
		self.__connect_signals()
	
	def __layout(self):
		# Widget creation
		vbox                = gtk.VBox()
		tool                = gtk.Toolbar()
		self.statusbar      = gtk.Statusbar()
		self.status_context = self.statusbar.get_context_id('MainWindow')
		self.container      = gtk.Viewport()
		self.config_dialog  = drawer.ConfigDialog('Configuration Dialog', self)
		self.connect_btn    = gtk.ToggleToolButton(gtk.STOCK_CONNECT)
		self.save_btn       = gtk.ToolButton(gtk.STOCK_SAVE)
		self.configure_btn  = gtk.ToolButton(gtk.STOCK_PREFERENCES)
		
		# Packing
		tool.insert(self.connect_btn, -1)
		tool.insert(gtk.SeparatorToolItem(), -1)
		tool.insert(self.save_btn, -1)
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
		else:
			btn.set_stock_id(gtk.STOCK_CONNECT)
			self.connect_btn.set_tooltip_markup("Connect")

	def __configure_clicked(self, btn):
		response = self.config_dialog.run()
		print response, self.config_dialog.get_config()
		self.config_dialog.hide()
	
	def __quit(self, window):
		gtk.main_quit()



if __name__ == "__main__":
	MainWindow()
	gtk.main()

class Main:
	
	def __init__(self, file):
		
		# The shared data list
		self.data = []
		
		# Configuration
		self.conf = Conf()
		
		# Reader & Drawer
		self.reader = None
		self.drawer = None
		
		# The properties dialog window
		self.props = Props(file, self.conf)
		
		# Main GUI
		self.gui = glade.XML(file, "window_main")
		self.gui.signal_autoconnect(self)
		self.window = self.gui.get_widget('window_main')
		self.props.dialog.set_transient_for(self.window)
		self.connect_btn = self.gui.get_widget('tool_connect')
		
		status = self.gui.get_widget('statusbar')
		self.statusbar = (status.get_context_id('main'), status)
		self.set_status_message('Disconnected')
	
	
	
	def start(self):
		
		"""
		Starts plotting data
		"""
		try:
			# TODO: Select appropriate reader according to "conf.source"
			print self.conf.source
			if self.conf.source == SPY:
				self.conn = serial.Serial( ** self.conf.serial() )
				self.reader = reader.ProbeReader(self.conn, self.data, 18)
			elif self.conf.source == FAKE_READER:
				self.reader = reader.FakeReader(self.data, 1)
			
			# Swap the label with the plotter
			container = self.gui.get_widget('container')
			container_lbl = self.gui.get_widget('container_label')
			if container_lbl:
				container.remove(container_lbl)
			self.drawer = drawer.ProbePlotter(self.data)
			container.add(self.drawer)
			self.drawer.show()
			
			self.reader.start()
			self.drawer.init_anim(66)
			self.set_status_message("Connected")
			
		except SerialException, e:
			print 'Error:', e.message
			self.set_status_message('Error: '+e.message)
			error = gtk.MessageDialog(self.window, type = gtk.MESSAGE_ERROR)
			error.set_markup(e.message)
			error.format_secondary_text('foo')
			error.format_secondary_markup('bar')
			error.show()
			self.connect_btn.set_active(False)
			
	
	
	def stop(self):
		if self.drawer:
			container = self.gui.get_widget('container')
			container.remove(self.drawer)
			self.drawer.stop_anim()
			self.reader.running = False
			self.set_status_message("Disconnected")
	
	def set_status_message(self, msg):
		"""
		Set the status bar message
		"""
		id, bar = self.statusbar
		bar.pop(id)
		bar.push(id, msg)
	
	#--------------------------------------------------------------------------
	# Signals Handlers
	#--------------------------------------------------------------------------
	def on_window_main_delete_event(self, window, event):
		try:
			self.reader.running = False
			self.reader.join()
		except:
			pass
		gtk.main_quit()

	def on_tool_properties_clicked(self, button):
		self.props.show()
	
	def on_tool_save_clicked(self, button):
		print 'save'
	
	def on_tool_connect_toggled(self, button):
		if button.get_active():
			self.start()
		else:
			self.stop()


