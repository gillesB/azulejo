import wnck, gtk
from collections import deque
import time
import keybinder
import configuration



maximized_window_geometry = gtk.gdk.get_default_root_window().property_get('_NET_WORKAREA')[2][:4]
upper_corner = maximized_window_geometry[:2]
screen_width = maximized_window_geometry[2]
screen_height = maximized_window_geometry[3]


'''because window resizing is not accurate we need a quick dirty workaround'''
window_geometry_error_margin = 30

geometry_to_use_index = 0

#variable to hold the amount of windows since the last arrangement
arrangement_size = 0


def get_all_windows():
    def f_normal_window(window):
        if window.get_window_type() == wnck.WindowType.__enum_values__[0]:
            return True
        return False

    s = wnck.screen_get_default()

    while gtk.events_pending():
        gtk.main_iteration()

    windows = s.get_windows_stacked()
    filtered_windows = filter(f_normal_window, windows)
    filtered_windows.reverse()
    return filtered_windows


def parse_simple_math_expressions(expression):
    expression = str(expression)
    expression = expression.replace('w', str(screen_width))
    expression = expression.replace('h', str(screen_height))
    return eval(expression)



def parse_geometry(geometry):
    return map(parse_simple_math_expressions, geometry)



def parse_arrangement(arrangement):
    return map(parse_geometry, arrangement)


def resize_windows(keybind, arrangement):
    global arrangement_size
    arrangement_numeric = parse_arrangement(arrangement)
    filtered_windows = get_all_windows()
    amount_of_windows = len(filtered_windows)     
    
    if amount_of_windows < len(arrangement_numeric):
        arrangement_numeric = arrangement_numeric[:amount_of_windows]
  
    i = 0
    arrangement_size = len(arrangement_numeric) #global scope variable, also used to rotate windows
    while i < arrangement_size:
        geometry_list_args = [0, 255]
        index = arrangement_size - (i + 1) #we must start in the end in order to keep window order correct
        geometry_list_args.extend(map (int, arrangement_numeric[index]))
        filtered_windows[index].unmaximize()
        filtered_windows[index].set_geometry(*geometry_list_args)
        i += 1


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

    geometry_list_args.extend(map (int, geometries_numeric[geometry_to_use_index]))
    window.unmaximize()
    
    #add the upper corner to the position of the window
    #e.g. position 0,0 is somewhere in the upper panel, so the window has to be positioned just below the panel  
    geometry_list_args[0] += upper_corner[0]
    geometry_list_args[1] += upper_corner[1]
    
    #subtract frame width from window size
    window_frame_widths = window.property_get("_NET_FRAME_EXTENTS")[2]
    window_frame_width_left_and_right = window_frame_widths[0] + window_frame_widths[1]
    geometry_list_args[2] -= window_frame_width_left_and_right
    
    window_frame_width_top_and_bottom = window_frame_widths[2] + window_frame_widths[3]
    geometry_list_args[3] -= window_frame_width_top_and_bottom
    
    window.move_resize(*geometry_list_args)



def rotate_windows(keybind, dummy):
    global arrangement_size
    windows = get_all_windows()
    amount_of_windows = len(windows)
    
    if amount_of_windows > arrangement_size:
        windows = windows[:arrangement_size]
        
    geos = []
    for window in windows:
        window_geo = window.get_geometry()
        window_geo = window_geo[:4]
        geos.append(window_geo)
        
        #do the actual rotations, lets use deque as it's dramatically more efficient than a trivial shift implementation
    windows_deq = deque(windows)
    windows_deq.rotate(1)
      
    rotation_len = len(windows_deq)
    i = 0
    while i < rotation_len:
        geometry_list_args = [0, 255]
        index = rotation_len - (i + 1) #again, start by the tail
        geometry_list_args.extend(map (int, geos[index]))
        windows_deq[index].unmaximize()
        windows_deq[index].set_geometry(*geometry_list_args)
        i += 1
    
    #(windows_deq[0]).activate(int(time.time())) #not sure why it doesn't work. if uncommented causes other windows beyond the rotated ones to hide behind current ones even after pressing ctrl+tab

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
    wnck.screen_get_default().force_update() #doesn't appear to do much
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
