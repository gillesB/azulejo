from collections import deque
import gtk
import keybinder
import configuration
import operator
import pynotify
from Window import Window

from Xlib.display import Display
from Xlib import X


_display = Display()
_root_window = _display.screen().root
_atom = _display.intern_atom
_workarea = _root_window.get_full_property(_atom("_NET_WORKAREA"), X.AnyPropertyType).value
#maximized_window_geometry = gtk.gdk.get_default_root_window().property_get('_NET_WORKAREA')[2][:4]
upper_corner = _workarea[:2]
screen_width = _workarea[2]
screen_height = _workarea[3]

geometry_to_use_index = 0
windows_deq = deque()
windows_geo = []

def get_normal_windows_on_current_desktop():
    def m_get_window_from_XID(XID):
        return Window(XID)
    
    def f_normal_window(window):
        if window_is_on_current_desktop(window) and window_is_window_type_normal(window):
            return True
        return False
    
    XIDs = _root_window.get_full_property(_atom("_NET_CLIENT_LIST_STACKING"), X.AnyPropertyType).value
    windows = map(m_get_window_from_XID, XIDs)
    filtered_windows = filter(f_normal_window, windows)
    filtered_windows.reverse()
    return filtered_windows

def window_is_on_current_desktop(window):
    assert isinstance(window, Window)
    current_desktop = _root_window.get_full_property(_atom("_NET_CURRENT_DESKTOP"), X.AnyPropertyType).value[0]
    if current_desktop == window.is_on_desktop():
            return True
    return False

def window_is_window_type_normal(window):
    assert isinstance(window, Window)
    if window.get_window_type() == _atom("_NET_WM_WINDOW_TYPE_NORMAL"):
            return True
    return False

def parse_simple_math_expressions(expression):
    expression = str(expression)
    expression = expression.replace('w', str(screen_width))
    expression = expression.replace('h', str(screen_height))
    return eval(expression)

def parse_geometry(geometry):
    return map(parse_simple_math_expressions, geometry)

def parse_arrangement(arrangement):
    return map(parse_geometry, arrangement)

def move_single_window(keybind, geometries):   
    active_window = get_active_window()
    assert isinstance(active_window, Window)
    
    window_geometry = active_window.get_geometry()
    window_width = window_geometry["width"]
    window_height = window_geometry["height"]

    print geometries[0]
    active_window.move(eval(geometries[0]), eval(geometries[1]))

def get_active_window():
    XID = _root_window.get_full_property(_atom("_NET_ACTIVE_WINDOW"), 0).value[0]
    return Window(XID)

resize_old_keybind = ""
def resize_single_window(keybind, geometries):
    global geometry_to_use_index, resize_old_keybind
    window = get_active_window()
    assert isinstance(window, Window) 

    #not an arrangement, but a list of geometries for that matter
    #geometry consists of the position X, position Y, width, height 
    geometries_numeric = parse_arrangement(geometries)
    geometry_list_args = []
    
    if resize_old_keybind == keybind:
        geometry_to_use_index = (geometry_to_use_index + 1) % len(geometries_numeric)
    else:
        resize_old_keybind = keybind    
        geometry_to_use_index = 0

    geometry = map (int, geometries_numeric[geometry_to_use_index])
    __move_and_resize_window(window, geometry)

resize_old_keybind = ""
def tile_windows(keybind, arrangement):
    global windows_deq, windows_geo, resize_old_keybind

    #fetch the needed data
    arrangement_numeric = parse_arrangement(arrangement)
    windows = get_normal_windows_on_current_desktop()
    amount_of_windows = len(windows)  
    
    if amount_of_windows < len(arrangement_numeric):
        arrangement_numeric = arrangement_numeric[:amount_of_windows]
        
    #if the same windows should be tiled a second time, simply rotate them
    if keybind == resize_old_keybind:
        same_windows = True
        for i in range(len(arrangement_numeric)):
            if windows[i] not in windows_deq:
                same_windows = False
                break
        if same_windows:
            rotate_windows(None, None)
            return
    else:
        resize_old_keybind = keybind   
  
    #tile the windows
    windows_deq.clear()
    windows_geo = []   
    
    i = 0
    arrangement_size = len(arrangement_numeric)
    while i < arrangement_size:
        index = i
        geometry = map (int, arrangement_numeric[index])
        __move_and_resize_window(windows[index], geometry)
        windows_deq.append(windows[index])
        windows_geo.append(geometry)
        i += 1
    
    #sort geometries of windows in such way, that they will rotate clockwise    
    windows_geo.sort(key=operator.itemgetter(0, 1))
    if(len(windows_geo) == 4):
        windows_geo_clone = windows_geo[::]
        windows_geo[1] = windows_geo_clone[2]
        windows_geo[2] = windows_geo_clone[3]
        windows_geo[3] = windows_geo_clone[1]
    print windows_geo

def __move_and_resize_window(window, geometry):
    assert isinstance(window, Window)
    geometry_clone = geometry[::]

    #window.unmaximize()
    
    #add the upper corner to the position of the window
    #e.g. position 0,0 is somewhere in the upper panel, so the window has to be positioned just below the panel  
    geometry_clone[0] += upper_corner[0]
    geometry_clone[1] += upper_corner[1]
    
    window.move_and_resize(*geometry_clone)
    
def rotate_windows(keybind, dummy):
        
    rotation_len = len(windows_deq)
    i = 0
    while i < rotation_len:
        window = windows_deq[i]
        geometry = windows_geo[(i + 1 + rotation_len) % rotation_len] 
        __move_and_resize_window(window, geometry)
        i += 1 
        
    windows_deq.rotate()

bound_keys = []
def bind_keys(get_config_data_function):
    for action in get_config_data_function():
        keybinds = action['keybind']
        function_name = action['function']
        function = callable_actions[function_name]
        parameters = action['parameters']
        dispacher_parameters = [function, keybinds, parameters]        
        
        for keybind in keybinds:
            if keybinder.bind(keybind, dispatcher , dispacher_parameters):
                bound_keys.append(keybind)
            else:
                print keybind, "was not bound successfully"    

def unbind_keys():
    global bound_keys
    for keystring in bound_keys:
        keybinder.unbind(keystring)
    bound_keys = []
    
def switch_config_files():
    filename = configuration.switch_shortcut_file()
    unbind_keys()
    bind_keys(configuration.get_config_data)
    notification = pynotify.Notification("Switched Shortcuts", "switched to file: " + filename)
    notification.set_urgency(pynotify.URGENCY_LOW)
    notification.set_timeout(2000)
    notification.show()    

def print_window_info():
    window = get_active_window()
    assert isinstance(window, Window)
    window_geometry = window.get_geometry()
    print "Window title: ", window.get_name()
    print "Window width and height", window_geometry["width"], window_geometry["height"] , "+ frame size: ", window.get_frame_extents()
    print "Window position", window_geometry["x"], window_geometry["y"]

callable_actions = dict(\
    resize_single_window=resize_single_window, \
    tile_windows=tile_windows, \
    rotate_windows=rotate_windows, \
    move_single_window=move_single_window, \
    switch_config_files=switch_config_files
)

def dispatcher(dis_param):       
    func = dis_param[0]
    keybind = dis_param[1]
    param = dis_param[2]
    func(keybind, param)    
   
   
def run():
    print "Usable screen size: ", screen_width, "x" , screen_height
    pynotify.init("Azulejo")

    keybinder.bind("<Super>y", print_window_info)
    keybinder.bind("<Super>c", switch_config_files)       

    bind_keys(configuration.get_config_data_first_time)
    
    gtk.main()    
