from Xlib.display import Display
from Xlib import X


class Workarea(object):
    '''
    This class contains some utils methods to simplify setting the Extended Window Manager Hints (EWMH).
    Especially the property "_NET_WORKAREA" is important, as it fetches the size of the current desktop,
    without status bars or dock bars. Thus it returns the usable space for 'normal' windows, called workarea.

    The downside of this approach is, that it works only if one screen is connected. If two or more screens are
    connected, they will be handled as one big screen. The returned size is not usable, as the individual screens may
    have different resolutions and different status bars and dock bars. Therefore an other approach to detect the
    workarea of each screen is needed.
    '''
    __display = Display()
    _root_window = __display.screen().root
    atom = __display.intern_atom
    _workarea = _root_window.get_full_property(atom("_NET_WORKAREA"), X.AnyPropertyType).value
    #upper_corner = _workarea[:2]
    #screen_width = _workarea[2]
    #screen_height = _workarea[3]    


    @staticmethod
    def get_all_XIDs():
        """
        Returns all IDs of the windows of the X server. These IDs are called XIDs.

        :return: all XIDs
        :rtype: list
        """
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_CLIENT_LIST_STACKING"),
                                                       X.AnyPropertyType).value

    @staticmethod
    def get_current_desktop():
        """
        The index of the current desktop. This is always an integer between 0 and _NET_NUMBER_OF_DESKTOPS - 1.

        :return: index of the current desktop
        :rtype: int
        """
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value[
            0]

    @staticmethod
    def get_workarea_width():
        """
        Returns the workarea width.

        :return: the workarea width
        :rtype: int
        """
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_WORKAREA"), X.AnyPropertyType).value[2]

    @staticmethod
    def get_workarea_height():
        """
        Returns the workarea height.

        :return: the workarea height
        :rtype: int
        """
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_WORKAREA"), X.AnyPropertyType).value[3]

    @staticmethod
    def get_upper_corner():
        """
        Returns the left upper corner of the workarea relative to the desktop.

        :return: the left upper corner of the workarea
        :rtype: list
        """
        return Workarea._root_window.get_full_property(Workarea.atom("_NET_WORKAREA"), X.AnyPropertyType).value[:2]

    @staticmethod
    def get_upper_corner_X():
        """
        Returns the X coordinate of the left upper corner of the workarea, relative to the desktop.

        :return: the X coordinate of the upper corner of the workarea
        :rtype: int
        """
        return Workarea.get_upper_corner()[0]

    @staticmethod
    def get_upper_corner_Y():
        """
        Returns the Y coordinate of the left upper corner of the workarea, relative to the desktop.

        :return: the Y coordinate of the upper corner of the workarea
        :rtype: int
        """
        return Workarea.get_upper_corner()[1]

    @staticmethod
    def get_root():
        """
        Returns the root window of the current X screen. Usually there is only one X screen as multiscreen support is
        provided by an X server extension.
        E.g. RandR

        :return: the root window
        :rtype: Xlib.display.Window
        """
        return Workarea._root_window

    @staticmethod
    def get_display():
        """
        Returns the X display

        :return: the X display
        :rtype: Xlib.display.Display
        """
        return Workarea.__display


    def __init__(self):
        pass
        '''
        Constructor
        '''
        