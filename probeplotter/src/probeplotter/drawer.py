"""
 " Provides classes to animate on a gtk.DrawingArea.
 """

import gtk
import gobject

class Stage(gtk.DrawingArea):
    """
     " The Stage.
     """
    def __init__(self, clear_color = (1, 1, 1)):
        """
         " Creates a new plot area.
         """
        gtk.DrawingArea.__init__(self)
        self.connect("expose-event", self._on_expose_event)
        self.clear_color = clear_color
        self.time = 0
        # Private
        self._anim = False
    
    def draw(self, ctx, width, height):
        """
         " Override this method to draw on the Stage.
         """
        pass
    
    def on_anim(self, t):
        """
         " Override this method. Fired whenever an animation frame is reached.
         """
        pass
    
    def init_anim(self, interval):
        """
         " Initiates the animation with given interval between frames.
         """
        self.time = 0
        self._anim = True
        gobject.timeout_add(interval, self._animate)
    
    def stop_anim(self):
        """
         " Stops the animation.
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