"""

This module provides methods and classes for
reading the Serial port and retrieving its data.

"""

from threading import Thread, Event, Lock
import random
import time

class SerialLineReader(Thread):
	
    """
    Reads from conn serial port handler in a separate thread.
    """

    def __init__(self, conn):
    	
        """
        @param conn: The serial port handler.
        """
        Thread.__init__(self)
        self.conn = conn
        self.running = False
        self.paused = True
        self.event = Event()
        self.pause_lock = Lock()
    
    def on_data(self, data):
    	
        """
        Override this method to process data.
        """
        pass
    
    def pause(self):
    	
    	"""
    	Stops reading from source.
    	"""
        self.pause_lock.acquire()
        self.paused = True
        self.pause_lock.release()
    
    def resume(self):
    	
    	"""
    	Resumes reading from sources.
    	"""
        self.event.set()
        self.event.clear()
    
    def run(self):
    	
        """
        Starts the reader thread.
        """
        buff = ""
        self.paused = False
        self.running = True
        while self.running:
            if self.paused:
                self.event.wait()
                self.paused = False
            else:
                self.pause_lock.acquire()
                char = self.conn.read(1)
                if char == "\r":
                    self.on_data(buff)
                    buff = ""
                else:
                    buff += char
                self.pause_lock.release()



class ProbeReader(SerialLineReader):
	
	"""
	
	This class provides methods to read from a probe with
	a specific data length and maximum points. The points
	which exceed this value are dropped out of the shared_list.
	
	"""
	
	def __init__(self, conn, shared_list, data_len, max_points = 100):
		
		"""
		@param conn: The serial port connection.
		@param shared_list: A list where the data is written.
		@param data_len: The length of the data. Every data out of this length is dropped.
		@param max_points: The maximum points in this shared_list
		"""
		SerialLineReader.__init__(self, conn)
		self.data_len = data_len
		self.shared_list = shared_list
		self.max_points = max_points
		self.output = None
	
	def set_output(self, fileName):
		
		"""
		Sets the output for this reader. Every time a valid data is received,
		it is written to this output file.
		"""
		self.output = open(fileName, "w")
	
	# Override
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



class FakeReader(Thread):
	
	"""
	
	This is a fake reader, which writes a random value
	into the data list in a determined interval time.
	
	"""
	
	def __init__(self, data, interval):
		
		"""
		@param data: The shared_list.
		@param interval: The interval in which this fake reader writes into the list.
		"""
		Thread.__init__(self)
		self.interval = interval
		self.data = data
		self.running = False
	
	# Override
	def run(self):
		
		"""
		Runs the fake reader.
		"""
		i = 0
		self.running = True
		while self.running:
			self.data.append((i, random.random() * 10))
			if len(self.data) > 100:
				self.data.pop(0)
			i += 1
			time.sleep(self.interval)
