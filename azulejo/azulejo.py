import gtk
from collections import deque
import time
import keybinder
import configuration
import operator
import pynotify

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

def __move_and_resize_window(window, geometry):
    geometry_clone = geometry[::]

    window.unmaximize()
    
    #add the upper corner to the position of the window
    #e.g. position 0,0 is somewhere in the upper panel, so the window has to be positioned just below the panel  
    geometry_clone[0] += upper_corner[0]
    geometry_clone[1] += upper_corner[1]
    
    #subtract frame width from window size
    window_frame_widths = __get_frame_widths_of_window(window)
    window_frame_width_left_and_right = window_frame_widths[0] + window_frame_widths[1]
    geometry_clone[2] -= window_frame_width_left_and_right
    
    window_frame_width_top_and_bottom = window_frame_widths[2] + window_frame_widths[3]
    geometry_clone[3] -= window_frame_width_top_and_bottom
    
    window.move_resize(*geometry_clone)
    
def __get_frame_widths_of_window(window):
    #sometimes the frame widths is not known
     ewmh_frame = window.property_get("_NET_FRAME_EXTENTS")
     if (ewmh_frame != None):
         return ewmh_frame[2]
     else:
         return [0, 0, 0, 0]

def rotate_windows(keybind, dummy):
        
    rotation_len = len(windows_deq)
    i = 0
    while i < rotation_len:
        window = windows_deq[i]
        geometry = windows_geo[(i + 1 + rotation_len) % rotation_len] 
        __move_and_resize_window(window, geometry)
        i += 1 
        
    windows_deq.rotate(1)

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
    window = gtk.gdk.screen_get_default().get_active_window()
    assert isinstance(window, gtk.gdk.Window)
    print "Window title: ", window.property_get('_NET_WM_NAME')
    print "Window size: ", window.get_size(), "+ frame size: ", __get_frame_widths_of_window(window)
    print "Window position", window.get_position()

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
   
bound_keys = []
    
def run():
    global bound_keys
    print "Usable screen size: ", screen_width, "x" , screen_height
    pynotify.init("Azulejo")

    keybinder.bind("<Super>i", print_window_info)
    keybinder.bind("<Super>c", switch_config_files)       

    bind_keys(configuration.get_config_data_first_time)       
              
    gtk.main()
