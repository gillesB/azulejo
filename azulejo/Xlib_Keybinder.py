from Xlib.display import Display
from Xlib import X, XK
import sys

class Xlib_Keybinder(object):
    '''
    classdocs
    '''


    def __init__(self):
        # current display
        self.display = Display()
        root = self.display.screen().root

        # we tell the X server we want to catch keyPress event
        root.change_attributes(event_mask = X.KeyPressMask)
            
    def bind(self,keystring, callback, user_data):
        codes = keystring.split('+')
        mods = codes[:-1]
        key = codes[-1]        
        
        keycode = self.generate_keycode(key)
        modmask = self.generate_modmask(mods)
        
        # Tell X we want to hear about it when this key is pressed...
        try:
            self.grab_key(keycode, modmask)
            self.register_hotkey(keycode, modmask, callback)
            return True
        except:
            return False
        
    def handle_event(self,aEvent):
        
        
        
        
    #
    # Takes a string representation of a key and turns it into a key code for
    # use with grab_key. See Xlib/keysymdef/latin1.py and
    # Xlib/keysymdef/miscellany.py for available key code strings.
    #
    def generate_keycode(self, key):
        return self.display.keysym_to_keycode(XK.string_to_keysym(key))

    #
    # Takes a list of string modifiers and converts them to their proper mask
    # form. Essentially the equivalent of generate_keycode for key modifiers.
    # Currently the only modifiers supported are Shift, Ctrl, Alt, and Super.
    #
    def generate_modmask(self, mods):
        modmask = 0
        if len(mods) >= 1:
            for mod in mods:
                if mod == 'Shift':
                    modmask = modmask | X.ShiftMask
                elif mod == 'Ctrl':
                    modmask = modmask | X.ControlMask
                elif mod == 'Alt':
                    modmask = modmask | X.Mod1Mask
                elif mod == 'Super':
                    modmask = modmask | X.Mod4Mask
                else:
                    print >> sys.stderr, "Could not use modifier %s" % mod
        else:
            modmask = X.AnyModifier

        return modmask
    
    #
    # Another one that took forever to figure out. Grabbing a key *itself* is
    # pretty straight-forward. Unfortunately, I had number lock on. Ug. So
    # for each key we want to grab, we need to grab it normally, and then we
    # need to grab it three more times with the following masks:
    #    Mod2Mask (Number lock)
    #    LockMask (Caps lock)
    #    Mod2Mask | LockMask (Number lock and Caps lock)
    #
    # What about scroll lock? o_O
    #
    def grab_key(self, keycode, mask):
        self.get_root().grab_key(keycode, mask, 1, X.GrabModeAsync, X.GrabModeAsync)
        self.get_root().grab_key(keycode, mask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
        self.get_root().grab_key(keycode, mask | X.LockMask, 1, X.GrabModeAsync, X.GrabModeAsync)
        self.get_root().grab_key(keycode, mask | X.Mod2Mask | X.LockMask, 1, X.GrabModeAsync, X.GrabModeAsync)
        
    #
    # Simply ties a key code to a callback method in the Tile class. Valid key codes
    # can be found in the documentation provided. (But are based on the key symbols
    # defined in Xlib. Probably in Xlib/keysymdef/latin1.py and Xlib/keysymdef/miscellany.py)
    # 
    @staticmethod
    def register_hotkey(keycode, mask, callback):
        if not keycode in Xlib_Keybinder._DISPATCHER:
            Xlib_Keybinder._DISPATCHER[keycode] = {}
        Xlib_Keybinder._DISPATCHER[keycode][mask] = callback     
        
        