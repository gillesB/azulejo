'''
Created on Jul 12, 2012

@author: me
'''
from Window import Window
from Workarea import Workarea

class WindowFetcher(object):
    def get_normal_windows_on_current_desktop(self):
        def m_get_window_from_XID(XID):
            return Window(XID)
        
        def f_normal_window(window):
            if self.window_is_on_current_desktop(window) and self.window_is_window_type_normal(window):
                return True
            return False
        
        XIDs = Workarea.get_all_XIDs()
        windows = map(m_get_window_from_XID, XIDs)
        filtered_windows = filter(f_normal_window, windows)
        filtered_windows.reverse()
        return filtered_windows
    
    def window_is_on_current_desktop(self, window):
        assert isinstance(window, Window)
        if Workarea.get_current_desktop() == window.is_on_desktop():
                return True
        return False
    
    def window_is_window_type_normal(self, window):
        assert isinstance(window, Window)
        if window.get_window_type() == Workarea._atom("_NET_WM_WINDOW_TYPE_NORMAL"):
                return True
        return False


    def __init__(self, params):
        '''
        Constructor
        '''
        