from Xlib.display import Display
import operator
from Xlib import X
from Window import Window
from collections import deque


class Workarea(object):
    '''
    classdocs
    '''
    __display = Display()
    _root_window = __display.screen().root
    atom = __display.intern_atom
    _workarea = _root_window.get_full_property(_atom("_NET_WORKAREA"), X.AnyPropertyType).value
    upper_corner = _workarea[:2]
    screen_width = _workarea[2]
    screen_height = _workarea[3]
    windows_deq = deque()
    windows_geo = []
    geometry_to_use_index = 0
    
    def parse_simple_math_expressions(self, expression):
        expression = str(expression)
        expression = expression.replace('w', str(self.screen_width))
        expression = expression.replace('h', str(self.screen_height))
        return eval(expression)

    def parse_geometry(self,geometry):
        return map(self.parse_simple_math_expressions, geometry)
    
    def parse_arrangement(self,arrangement):
        return map(self.parse_geometry, arrangement)
    
    def get_active_window(self):
        XID = self._root_window.get_full_property(self._atom("_NET_ACTIVE_WINDOW"), 0).value[0]
        return Window(XID)
    
    def move_single_window(self, keybind, geometries):   
        active_window = self.get_active_window()
        assert isinstance(active_window, Window)
        
        window_geometry = active_window.get_geometry()
        window_width = window_geometry["width"]
        window_height = window_geometry["height"]
    
        print geometries[0]
        active_window.move(eval(geometries[0]), eval(geometries[1]))
        
    resize_old_keybind = ""
    def resize_single_window(self, keybind, geometries):
        window = self.get_active_window()
        assert isinstance(window, Window) 
    
        #not an arrangement, but a list of geometries for that matter
        #geometry consists of the position X, position Y, width, height 
        geometries_numeric = self.parse_arrangement(geometries)
        
        if self.resize_old_keybind == keybind:
            geometry_to_use_index = (self.geometry_to_use_index + 1) % len(geometries_numeric)
        else:
            self.resize_old_keybind = keybind    
            geometry_to_use_index = 0
    
        geometry = map (int, geometries_numeric[geometry_to_use_index])
        window.move_and_resize(*geometry)
        
    resize_old_keybind = ""
    def tile_windows(self, keybind, arrangement):
    
        #fetch the needed data
        arrangement_numeric = self.parse_arrangement(arrangement)
        windows = self.get_normal_windows_on_current_desktop()
        amount_of_windows = len(windows)  
        
        if amount_of_windows < len(arrangement_numeric):
            arrangement_numeric = arrangement_numeric[:amount_of_windows]
            
        #if the same windows should be tiled a second time, simply rotate them
        if keybind == self.resize_old_keybind:
            same_windows = True
            for i in range(len(arrangement_numeric)):
                if windows[i] not in self.windows_deq:
                    same_windows = False
                    break
            if same_windows:
                self.rotate_windows(None, None)
                return
        else:
            resize_old_keybind = keybind   
      
        #tile the windows
        self.windows_deq.clear()
        windows_geo = []   
        
        i = 0
        arrangement_size = len(arrangement_numeric)
        while i < arrangement_size:
            index = i
            geometry = map (int, arrangement_numeric[index])
            windows[index].move_and_resize(*geometry)
            self.windows_deq.append(windows[index])
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
        
    def rotate_windows(self, keybind, dummy):
            
        rotation_len = len(self.windows_deq)
        i = 0
        while i < rotation_len:
            window = self.windows_deq[i]
            geometry = self.windows_geo[(i + 1 + rotation_len) % rotation_len] 
            window.move_and_resize(*geometry)
            i += 1 
            
        self.windows_deq.rotate()
      
    def print_window_info(self):
        window = self.get_active_window()
        assert isinstance(window, Window)
        window_geometry = window.get_geometry()
        print "Window title: ", window.get_name()
        print "Window width and height", window_geometry["width"], window_geometry["height"] , "+ frame size: ", window.get_frame_extents()
        print "Window position", window_geometry["x"], window_geometry["y"]               


    def __init__(self):
        pass
        '''
        Constructor
        '''
        