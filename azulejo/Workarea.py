from Xlib.display import Display
from Xlib import X
from Window import Window


class Workarea(object):
    '''
    classdocs
    '''
    __display = Display()
    _root_window = __display.screen().root
    _atom = __display.intern_atom
    _workarea = _root_window.get_full_property(_atom("_NET_WORKAREA"), X.AnyPropertyType).value
    upper_corner = _workarea[:2]
    screen_width = _workarea[2]
    screen_height = _workarea[3]
    
    @staticmethod
    def get_active_window():
        XID = Workarea._root_window.get_full_property(Workarea._atom("_NET_ACTIVE_WINDOW"), 0).value[0]
        return Window(XID)
    
    @staticmethod
    def print_window_info():
        window = Workarea.get_active_window()
        assert isinstance(window, Window)
        window_geometry = window.get_geometry()
        print "Window title: ", window.get_name()
        print "Window width and height", window_geometry["width"], window_geometry["height"] , "+ frame size: ", window.get_frame_extents()
        print "Window position", window_geometry["x"], window_geometry["y"]
     
    @staticmethod    
    def get_all_XIDs():
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_CLIENT_LIST_STACKING"), X.AnyPropertyType).value
    
    @staticmethod
    def get_current_desktop():
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value[0]
    
    @staticmethod
    def get_screen_width():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_WORKAREA"), X.AnyPropertyType).value[2]
    
    @staticmethod
    def get_screen_height():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_WORKAREA"), X.AnyPropertyType).value[3]   
    


    def __init__(self):
        pass
        '''
        Constructor
        '''
        