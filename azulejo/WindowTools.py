'''
Created on Jul 12, 2012

@author: gillesB
'''
from Window import Window
from Workarea import Workarea

class WindowTools(object):
    """
    Some utilities for the windows
    """

    @staticmethod
    def get_active_window():
        """
        Returns the active window

        :return: the active window
        :rtype: Window
        """
        XID = Workarea._root_window.get_full_property(Workarea.atom("_NET_ACTIVE_WINDOW"), 0).value[0]
        return Window(XID)
    
    @staticmethod
    def print_window_info(keybinding, param):
        """
        Prints some information of the currently active window.

        :param keybinding:
        :type keybinding:
        :param param:
        :type param:
        """

        window = WindowTools.get_active_window()
        assert isinstance(window, Window)
        window_geometry = window.get_geometry()
        print "Screen resolution: " 
        print "Workarea width and height: ", Workarea.get_workarea_width(), Workarea.get_workarea_height()
        print "Window title: ", window.get_name()
        print "Window width and height", window_geometry["width"], window_geometry["height"] , "+ frame size: ", window.get_frame_extents()
        print "Window position", window_geometry["x"], window_geometry["y"]    
    
    @staticmethod  
    def get_normal_windows_on_current_desktop():
        """
        Returns all 'normal' windows which are visible on the current desktop.

        :return: all 'normal' windows which are visible on the current desktop
        :rtype: list[Window]
        """
        def m_get_window_from_XID(XID):
            return Window(XID)
        
        def f_normal_window(window):
            if WindowTools.window_is_on_current_desktop(window) and WindowTools.window_is_window_type_normal(window):
                return True
            return False
        
        XIDs = Workarea.get_all_XIDs()
        windows = map(m_get_window_from_XID, XIDs)
        filtered_windows = filter(f_normal_window, windows)
        filtered_windows.reverse()
        return filtered_windows
        
    @staticmethod  
    def window_is_on_current_desktop(window):
        """
        Returns True if window is on current desktop, False otherwise

        :param window:
        :type window: Window
        :return: True if window is on current desktop, False otherwise
        :rtype: bool
        """
        if Workarea.get_current_desktop() == window.get_desktop_id():
                return True
        return False
    
    @staticmethod      
    def window_is_window_type_normal(window):
        """
        Returns True if window is a normal window, False otherwise

        :param window:
        :type window: Window
        :return: True if window is a normal window, False otherwise
        :rtype: bool
        """
        window_type = window.get_window_type()
        if (window_type == Workarea.atom("_NET_WM_WINDOW_TYPE_NORMAL")
            or (window_type is None and window.get_transient_for() is None)):
                return True
        return False


    def __init__(self, params):
        '''
        Constructor
        '''
        