
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


###
## CONSTANTS
###
CLT_SPY		= 1
MOD_4_20	= 2
SPY			= 3

class Conf:
	
	"""
	
	This class keeps some configurations
	for the program.
	It also should provide methods for
	saving those in a .ini file.
	
	"""
	
	def __init__(self):
		self.port = None
		self.source = SPY
		self.xonxoff = 1
		self.baudrate = 19200
	
	def serial(self):
		return {
			'port': self.port,
			'baudrate': self.baudrate,
			'xonxoff': self.xonxoff
		}

class Props:
	
	"""
	The properties Dialog from glade file. 
	"""
	
	def __init__(self, file, conf):
		
		"""
		@param file: The glade file path.
		@param conf: The configuration object.
		"""
		self.conf = conf
		self.gui = glade.XML(file, 'dialog_properties')
		self.gui.signal_autoconnect(self)
		self.dialog = self.gui.get_widget('dialog_properties')
		self.entry = self.gui.get_widget('dialog_port')
	
	def show(self):
		
		"""
		Shows this Properties Dialog.
		"""
		self.dialog.show()

	def hide(self):
		
		"""
		Hides this Properties Dialog
		"""
		self.dialog.hide()


	#--------------------------------------------------------------------------
	# Signals Handlers
	#--------------------------------------------------------------------------
	def on_dialog_properties_response(self, dialog, response):
		"""
		When Dialog receives a response.
		"""
		if response == 1: # OK
			self.conf.port = self.entry.get_text()
		self.hide()
		print self.conf
	
	def on_dialog_source_toggled(self, button):
		"""
		Updates the source from the users choice.
		"""
		print button.get_selected()

class Main:
	
	"""
	Main class.
	"""
	
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
		self.props.dialog.set_transient_for(window)
	
	
	
	def start(self):
		
		"""
		Starts plotting data
		"""
		try:
			self.conn = serial.Serial( ** self.conf.serial() )
			self.reader = serial.ProbeReader(self.conn, self.data, 18)
			self.reader.start()
			self.drawer.init_anim(66)
		except SerialException, msg:
			print 'Error:', msg
	
	#--------------------------------------------------------------------------
	# Signals Handlers
	#--------------------------------------------------------------------------
	def on_window_main_delete_event(self, window, event):
		gtk.main_quit()
        try:
    		self.reader.running = False
    		self.reader.join()
        except:
            pass

	def on_tool_properties_clicked(self, button):
		self.props.show()
	
	def on_tool_save_clicked(self, button):
		print 'save'

if __name__ == "__main__":
	main = Main('../../resources/gui.glade')
	window = main.gui.get_widget('window_main')
	window.show_all()
	gtk.main()
