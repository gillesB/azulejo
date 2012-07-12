'''
Created on Jul 12, 2012

@author: me
'''
from Window import Window
from Workarea import Workarea
from Xlib import X

class WindowFetcher(object):
    def get_normal_windows_on_current_desktop(self):
        def m_get_window_from_XID(XID):
            return Window(XID)
        
        def f_normal_window(window):
            if self.window_is_on_current_desktop(window) and self.window_is_window_type_normal(window):
                return True
            return False
        
        XIDs = self._root_window.get_full_property(Workarea.atom("_NET_CLIENT_LIST_STACKING"), X.AnyPropertyType).value
        windows = map(m_get_window_from_XID, XIDs)
        filtered_windows = filter(f_normal_window, windows)
        filtered_windows.reverse()
        return filtered_windows
    
    def window_is_on_current_desktop(self, window):
        assert isinstance(window, Window)
        current_desktop = self._root_window.get_full_property(Workarea.atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value[0]
        if current_desktop == window.is_on_desktop():
                return True
        return False
    
    def window_is_window_type_normal(self, window):
        assert isinstance(window, Window)
        if window.get_window_type() == Workarea.atom("_NET_WM_WINDOW_TYPE_NORMAL"):
                return True
        return False


    def __init__(self, params):
        '''
        Constructor
        '''
        