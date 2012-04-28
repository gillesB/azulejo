import gtk
from collections import deque
import time
import keybinder
import configuration
import operator

maximized_window_geometry = gtk.gdk.get_default_root_window().property_get('_NET_WORKAREA')[2][:4]
upper_corner = maximized_window_geometry[:2]
screen_width = maximized_window_geometry[2]
screen_height = maximized_window_geometry[3]

geometry_to_use_index = 0
windows_deq = deque()
windows_geo = []

def get_normal_windows_on_current_desktop():
    def m_get_window_from_XID(XID):
        return gtk.gdk.window_foreign_new(XID)
    
    def f_normal_window(window):
        if window_is_on_current_desktop(window) and window_is_window_type_normal(window):
            return True
        return False
    
    XIDs = gtk.gdk.get_default_root_window().property_get("_NET_CLIENT_LIST_STACKING")[2]
    windows = map(m_get_window_from_XID, XIDs)
    filtered_windows = filter(f_normal_window, windows)
    filtered_windows.reverse()
    return filtered_windows

def window_is_on_current_desktop(window):
    current_desktop = gtk.gdk.get_default_root_window().property_get("_NET_CURRENT_DESKTOP")[2][0]
    window_is_on_desktop = window.property_get('_NET_WM_DESKTOP')[2][0]
    if current_desktop == window_is_on_desktop:
            return True
    return False

def window_is_window_type_normal(window):
    window_type = window.property_get('_NET_WM_WINDOW_TYPE')[2][0]
    if window_type == "_NET_WM_WINDOW_TYPE_NORMAL":
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
    default_screen = gtk.gdk.screen_get_default()
    assert isinstance(default_screen, gtk.gdk.Screen)
    
    active_window = default_screen.get_active_window()
    assert isinstance(active_window, gtk.gdk.Window)
    
    window_size = active_window.get_size()
    window_width = window_size[0]
    window_height = window_size[1]

    active_window.move(eval(geometries[0]), eval(geometries[1]))

resize_old_keybind = ""
def resize_single_window(keybind, geometries):
    global geometry_to_use_index, resize_old_keybind
    window = gtk.gdk.screen_get_default().get_active_window()
    assert isinstance(window, gtk.gdk.Window)    

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

def resize_windows(keybind, arrangement):
    global windows_deq, windows_geo
    
    windows_deq.clear()
    windows_geo = []
    
    arrangement_numeric = parse_arrangement(arrangement)
    filtered_windows = get_normal_windows_on_current_desktop()
    amount_of_windows = len(filtered_windows)     
    
    if amount_of_windows < len(arrangement_numeric):
        arrangement_numeric = arrangement_numeric[:amount_of_windows]
  
    i = 0
    arrangement_size = len(arrangement_numeric) #global scope variable, also used to rotate windows
    while i < arrangement_size:
        index = i #arrangement_size - (i + 1) #we must start in the end in order to keep window order correct
        geometry = map (int, arrangement_numeric[index])
        __move_and_resize_window(filtered_windows[index], geometry)
        windows_deq.append(filtered_windows[index])
        windows_geo.append(geometry)
        i += 1
    
    #sort geometries of windows in such a way that, a clockwise rotation will be possible    
    windows_geo.sort(key=operator.itemgetter(0, 1))
    print windows_geo
    if(len(windows_geo) == 4):
        windows_geo_clone = windows_geo[::]
        windows_geo[1] = windows_geo_clone[2]
        windows_geo[2] = windows_geo_clone[3]
        windows_geo[3] = windows_geo_clone[1]

def __move_and_resize_window(window, geometry):

    geometry_clone = geometry[::]

    window.unmaximize()
    
    #add the upper corner to the position of the window
    #e.g. position 0,0 is somewhere in the upper panel, so the window has to be positioned just below the panel  
    geometry_clone[0] += upper_corner[0]
    geometry_clone[1] += upper_corner[1]
    
    #subtract frame width from window size
    window_frame_widths = window.property_get("_NET_FRAME_EXTENTS")[2]
    window_frame_width_left_and_right = window_frame_widths[0] + window_frame_widths[1]
    geometry_clone[2] -= window_frame_width_left_and_right
    
    window_frame_width_top_and_bottom = window_frame_widths[2] + window_frame_widths[3]
    geometry_clone[3] -= window_frame_width_top_and_bottom
    
    window.move_resize(*geometry_clone)

def rotate_windows(keybind, dummy):
    global windows_deq
    print windows_deq
    print windows_geo 
    
    rotation_len = len(windows_deq)
    i = 0
    while i < rotation_len:
        window = windows_deq[i]
        print i, (i + 1 + rotation_len) % rotation_len
        geometry = windows_geo[(i + 1 + rotation_len) % rotation_len] 
        __move_and_resize_window(window, geometry)
        i += 1 
        
    windows_deq.rotate(1)

def print_window_info():
    window = gtk.gdk.screen_get_default().get_active_window()
    assert isinstance(window, gtk.gdk.Window)
    print "Window title: ", window.property_get('_NET_WM_NAME')
    print "Window size: ", window.get_size(), "+ frame size: ", window.property_get("_NET_FRAME_EXTENTS")[2]
    print "Window position", window.get_position()

callable_actions = dict(\
    resize_single_window=resize_single_window, \
    resize_windows=resize_windows, \
    rotate_windows=rotate_windows, \
    move_single_window=move_single_window   
)

def dispatcher(dis_param):       
    func = dis_param[0]
    keybind = dis_param[1]
    param = dis_param[2]
    func(keybind, param)    
    
def run():
    print "Usable screen size: ", screen_width, "x" , screen_height

    keybinder.bind("<Super>i", print_window_info)

    for action in configuration.conf_data:
        keybinds = action['keybind']
        function_name = action['function']
        function = callable_actions[function_name]
        parameters = action['parameters']
        dispacher_parameters = [function, keybinds, parameters]        
        
        for keybind in keybinds:
            if not keybinder.bind(keybind, dispatcher , dispacher_parameters):
                print keybind, "was not bound successfully"
              

    gtk.main()
