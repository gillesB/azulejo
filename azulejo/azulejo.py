import gtk
import keybinder
import configuration
import pynotify
from Workarea import Workarea
from WindowHandler import WindowHandler
from WindowFetcher import WindowFetcher

def run():
    Azulejo()

class Azulejo:
    def bind_keys(self, get_config_data_function):
        for action in get_config_data_function():
            keybinds = action['keybind']
            function_name = action['function']
            function = self.callable_actions[function_name]
            parameters = action['parameters']
            dispacher_parameters = [function, keybinds, parameters]
            
            for keybind in keybinds:
                if keybinder.bind(keybind, self.dispatcher , dispacher_parameters):
                    self.bound_keys.append(keybind)
                else:
                    print keybind, "was not bound successfully"
    
    def unbind_keys(self):
        for keystring in self.bound_keys:
            keybinder.unbind(keystring)
        self.bound_keys = []
        
    def switch_config_files(self):
        filename = configuration.switch_shortcut_file()
        self.unbind_keys()
        self.bind_keys(configuration.get_config_data)
        notification = pynotify.Notification("Switched Shortcuts", "switched to file: " + filename)
        notification.set_urgency(pynotify.URGENCY_LOW)
        notification.set_timeout(2000)
        notification.show()
    
    def define_callable_actions(self):
        self.callable_actions = dict(\
            resize_single_window=WindowHandler.resize_single_window, \
            tile_windows=WindowHandler.tile_windows, \
            rotate_windows=WindowHandler.rotate_windows, \
            move_single_window=WindowHandler.move_single_window
        )
    
    def dispatcher(self, dis_param):
        func = dis_param[0]
        keybind = dis_param[1]
        param = dis_param[2]
        #clone the parameter otherwise the could be overwritten
        func(keybind, param[::])
       
       
    def __init__(self):
        self.bound_keys = []
        self.workarea = Workarea()
        self.define_callable_actions()
        #print "Usable screen size: ", screen_width, "x" , screen_height
        pynotify.init("Azulejo")
    
        keybinder.bind("<Super>y", WindowFetcher.print_window_info)
        keybinder.bind("<Super>c", self.switch_config_files)
    
        self.bind_keys(configuration.get_config_data_first_time)
        
        gtk.main() 