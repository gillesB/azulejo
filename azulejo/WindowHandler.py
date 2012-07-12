'''
Created on Jul 12, 2012

@author: me
'''
from Window import Window
from Workarea import Workarea
import operator
from GeometryParser import GeometryParser
from WindowFetcher import WindowFetcher
from collections import deque

class WindowHandler(object):
    '''
    classdocs
    '''
    
    resize_old_keybind = ""
    geometry_to_use_index = 0
    windows_deq = deque()
    windows_geo = []
    
    @staticmethod
    def move_single_window(keybind, geometries):   
        active_window = Workarea.get_active_window()
        assert isinstance(active_window, Window)
        
        window_geometry = active_window.get_geometry()
        window_width = window_geometry["width"]
        window_height = window_geometry["height"]
    
        print geometries[0]
        active_window.move(eval(geometries[0]), eval(geometries[1]))
        
    
    @staticmethod
    def resize_single_window(keybind, geometries):
        window = Workarea.get_active_window()
        assert isinstance(window, Window) 
    
        #not an arrangement, but a list of geometries for that matter
        #geometry consists of the position X, position Y, width, height 
        geometries_numeric = GeometryParser.parse_arrangement(geometries)
        
        if WindowHandler.resize_old_keybind == keybind:
            WindowHandler.geometry_to_use_index = (WindowHandler.geometry_to_use_index + 1) % len(geometries_numeric)
        else:
            WindowHandler.resize_old_keybind = keybind    
            WindowHandler.geometry_to_use_index = 0
    
        geometry = map (int, geometries_numeric[WindowHandler.geometry_to_use_index])
        print geometry
        window.move_and_resize(*geometry)
        

    @staticmethod
    def tile_windows(keybind, arrangement):
    
        #fetch the needed data
        arrangement_numeric = GeometryParser.parse_arrangement(arrangement)
        windows = WindowFetcher.get_normal_windows_on_current_desktop()
        amount_of_windows = len(windows)  
        
        if amount_of_windows < len(arrangement_numeric):
            arrangement_numeric = arrangement_numeric[:amount_of_windows]
            
        #if the same windows should be tiled a second time, simply rotate them
        if keybind == WindowHandler.resize_old_keybind:
            same_windows = True
            for i in range(len(arrangement_numeric)):
                if windows[i] not in WindowHandler.windows_deq:
                    same_windows = False
                    break
            if same_windows:
                WindowHandler.rotate_windows(None, None)
                return
        else:
            WindowHandler.resize_old_keybind = keybind   
      
        #tile the windows
        WindowHandler.windows_deq.clear()
        windows_geo = []   
        
        i = 0
        arrangement_size = len(arrangement_numeric)
        while i < arrangement_size:
            index = i
            geometry = map (int, arrangement_numeric[index])
            windows[index].move_and_resize(*geometry)
            WindowHandler.windows_deq.append(windows[index])
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
    
    @staticmethod    
    def rotate_windows(keybind, dummy):
            
        rotation_len = len(WindowHandler.windows_deq)
        i = 0
        while i < rotation_len:
            window = WindowHandler.windows_deq[i]
            geometry = WindowHandler.windows_geo[(i + 1 + rotation_len) % rotation_len] 
            window.move_and_resize(*geometry)
            i += 1 
            
        WindowHandler.windows_deq.rotate()


    def __init__(self):
        '''
        Constructor
        '''
        