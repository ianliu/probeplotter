"""
 " This module provides methods and classes for
 " reading the Serial port and retrieving its data.
 """

from threading import Thread, Event, Lock

class SerialLineReader(Thread):
    """
     " Reads from conn serial port handler in a separate thread.
     """

    def __init__(self, conn):
        """
         " @param conn: The serial port handler.
         """
        Thread.__init__(self)
        self.conn = conn
        self.running = False
        self.paused = True
        self.event = Event()
        self.pause_lock = Lock()
    
    def on_data(self, data):
        """
         " Override this method to process data.
         """
        pass
    
    def pause(self):
        self.pause_lock.acquire()
        self.paused = True
        self.pause_lock.release()
    
    def resume(self):
        self.event.set()
        self.event.clear()
    
    def run(self):
        """
         " Starts the reader thread
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