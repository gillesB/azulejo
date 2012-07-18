from Xlib.display import Display
from Xlib import X, protocol
from Workarea import Workarea

class Window:
    """A wrapper class for Xlib Windows"""    
    
    __display = Display()
    __atom = __display.intern_atom
    __root_window = __display.screen().root

    
    def __init__(self, XID):
        self.XWindow = self.__display.create_resource_object("window", XID)
        
    def get_name(self):
        return self.get_property_value("_NET_WM_NAME")
       
    def get_frame_extents(self):
        extents = self.get_property_value("_NET_FRAME_EXTENTS")

        if extents != None:
            return extents
        else:
            return [0,0,0,0]
        
    def move(self,x,y):
        self.XWindow.configure(x=x, y=y)
        self.__display.flush()
        
    def is_on_desktop(self):
        return self.get_property_value("_NET_WM_DESKTOP")[0]
    
    def get_window_type(self):
        return self.get_property_value("_NET_WM_WINDOW_TYPE")[0]
        
    def get_property_value(self, name):
        propt = self.XWindow.get_full_property(self.__display.intern_atom(name), X.AnyPropertyType)
        if propt != None:
            return propt.value
        else:
            return None
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.XWindow == other.XWindow
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
            
        
        
    #------------------------------------------------------------------------------
    # COPIED METHODS
    # The following methods were copied and modified from PyTyle.
    # They were found in the file Probe.py
    #------------------------------------------------------------------------------
    
    #===============================================================================
    # PyTyle - A manual tiling manager
    # Copyright (C) 2009  Andrew Gallant <andrew@pytyle.com>
    #
    # This program is free software; you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation; either version 2 of the License, or
    # (at your option) any later version.
    #
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program; if not, write to the Free Software
    # Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    #===============================================================================

    #
    # It took me a little bit to figure this one out. So apparently, the
    # get_geometry window method returns coordinates that we don't care about.
    # (That is, they are relative to the root window?) So in order to
    # rectify this, we need to "translate" the x,y coordinates relative to
    # that root window. Not very intuitive at all. Kudos to wmctrl for showing
    # me the light here.
    #
    # Note: More testing has revealed different behavior for different window
    # managers here. For instance, with Compiz, we actually want the raw x,y
    # coordinates from get_geometry- translating them is bad! We end up with
    # some pretty big figures. (Viewports..?) I haven't investigated Compiz
    # thoroughly, but was able to get some minimal functionality by simply
    # removing the call to translate_coords.
    #
    def get_geometry(self):
        wingeom = self.XWindow.get_geometry()

        wintrans = self.XWindow.translate_coords(self.__root_window, wingeom.x, wingeom.y)
        wintrans.x = -wintrans.x
        wintrans.y = -wintrans.y

        #TODO: make this work for compiz
        # This is for compiz (and any other viewport-style WM?)...
        # looks like we don't need to translate
        """if self.is_compiz():
            viewport = self.get_viewport()
            if viewport:
                wintrans = wingeom
                wintrans.x += viewport['x']
                wintrans.y += viewport['y']"""

        return {'x': wintrans.x, 'y': wintrans.y, 'width': wingeom.width, 'height': wingeom.height}
    
    #
    # This simply "unmaximizes" or "restores" a window. We need to do this
    # every time we resize a window because it could have been maximized
    # by the user (which then could not be resized).
    #
    def reset(self):
        self._send_event(self.__atom("_NET_WM_STATE"), [0, self.__atom("_NET_WM_STATE_MAXIMIZED_VERT"), self.__atom("_NET_WM_STATE_MAXIMIZED_HORZ")])
        #win.change_property(self.atom("_NET_WM_STATE"), Xatom.ATOM, 32, [0, self.atom("_NET_WM_STATE_MAXIMIZED_VERT"), self.atom("_NET_WM_STATE_MAXIMIZED_HORZ")])
        self.__display.flush()

    #
    # Resizes the window with the given x/y/width/height pixel values.
    # Don't forget to flush after and reset the window before.
    #
    def move_and_resize(self, x, y, width, height):
        
        self.reset()
        
        x += Workarea.get_upper_corner_X()
        y += Workarea.get_upper_corner_Y()
        
        #subtract frame extents from window size
        frame_extents = self.get_frame_extents()
        width -= (frame_extents[0] + frame_extents[1])
        height -= (frame_extents[2] + frame_extents[3])

        # This is for compiz (and any other viewport-style WM?)...
        # looks like we don't need to translate
        #TODO: make this work for compiz
#        if self.is_compiz():
#            viewport = self.get_viewport()
#            if viewport:
#                x -= viewport['x']
#                y -= viewport['y']

        self.XWindow.configure(x=x, y=y, width=width, height=height)
        self.__display.flush()
        
    #
    # Another tricky one to figure out- this will allow you to send
    # a client message to the root window (necessary for removing
    # decorations, maximizing, etc).
    #
    # Props to PyPanel for this little snippet.
    #
    def _send_event(self, ctype, data, mask=None):
        data = (data + ([0] * (5 - len(data))))[:5]
        ev = protocol.event.ClientMessage(window=self.XWindow, client_type=ctype, data=(32, (data)))
        self.__root_window.send_event(ev, event_mask=X.SubstructureRedirectMask)    