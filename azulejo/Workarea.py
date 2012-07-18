from Xlib.display import Display
from Xlib import X


class Workarea(object):
    '''
    classdocs
    '''
    __display = Display()
    _root_window = __display.screen().root
    _atom = __display.intern_atom
    _workarea = _root_window.get_full_property(_atom("_NET_WORKAREA"), X.AnyPropertyType).value
    #upper_corner = _workarea[:2]
    #screen_width = _workarea[2]
    #screen_height = _workarea[3]    

     
    @staticmethod    
    def get_all_XIDs():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_CLIENT_LIST_STACKING"), X.AnyPropertyType).value
    
    @staticmethod
    def get_current_desktop():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value[0]
    
    @staticmethod
    def get_screen_width():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_WORKAREA"), X.AnyPropertyType).value[2]
    
    @staticmethod
    def get_screen_height():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_WORKAREA"), X.AnyPropertyType).value[3]
    
    @staticmethod
    def get_upper_corner():
        return Workarea._root_window.get_full_property(Workarea._atom("_NET_WORKAREA"), X.AnyPropertyType).value[:2]
    
    @staticmethod
    def get_upper_corner_X():
        return Workarea.get_upper_corner()[0]
    
    @staticmethod
    def get_upper_corner_Y():
        return Workarea.get_upper_corner()[1]
    
     
    


    def __init__(self):
        pass
        '''
        Constructor
        '''
        