'''
Created on Jul 12, 2012

@author: me
'''
from Window import Window
from Workarea import Workarea

class WindowFetcher(object):
    
    @staticmethod
    def get_active_window():
        XID = Workarea._root_window.get_full_property(Workarea.atom("_NET_ACTIVE_WINDOW"), 0).value[0]
        return Window(XID)
    
    @staticmethod
    def print_window_info():
        window = WindowFetcher.get_active_window()
        assert isinstance(window, Window)
        window_geometry = window.get_geometry()
        print "Window title: ", window.get_name()
        print "Window width and height", window_geometry["width"], window_geometry["height"] , "+ frame size: ", window.get_frame_extents()
        print "Window position", window_geometry["x"], window_geometry["y"]    
    
    @staticmethod  
    def get_normal_windows_on_current_desktop():
        def m_get_window_from_XID(XID):
            return Window(XID)
        
        def f_normal_window(window):
            if WindowFetcher.window_is_on_current_desktop(window) and WindowFetcher.window_is_window_type_normal(window):
                return True
            return False
        
        XIDs = Workarea.get_all_XIDs()
        windows = map(m_get_window_from_XID, XIDs)
        filtered_windows = filter(f_normal_window, windows)
        filtered_windows.reverse()
        return filtered_windows
        
    @staticmethod  
    def window_is_on_current_desktop(window):
        assert isinstance(window, Window)
        if Workarea.get_current_desktop() == window.is_on_desktop():
                return True
        return False
    
    @staticmethod      
    def window_is_window_type_normal(window):
        assert isinstance(window, Window)
        if window.get_window_type() == Workarea.atom("_NET_WM_WINDOW_TYPE_NORMAL"):
                return True
        return False


    def __init__(self, params):
        '''
        Constructor
        '''
        