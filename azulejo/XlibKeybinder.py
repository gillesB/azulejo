from Xlib.display import Display
from Xlib import X, XK
import sys
from Workarea import Workarea

class XlibKeybinder(object):
    '''
classdocs
'''


    def __init__(self):
        # current display
        self.display = Display()
        self.root = self.display.screen().root

        # we tell the X server we want to catch keyPress event
        self.root.change_attributes(event_mask = X.KeyPressMask)
            
    def bind(self,keystring, callback, user_data=None):
        
        #Split the keystring with the pattern <Mod>*Key into modifiers and key 
        codes = keystring.split('>')
        for i in range(len(codes)-1):
            codes[i] = codes[i][1:]
        mods = codes[:-1]
        key = codes[-1]
        
        # No key?
        if not key:
            print >> sys.stderr, "Could not map %s to %s" % (keystring, callback) 
            return False
        
        keycode = self.generate_keycode(key)
        modmask = self.generate_modmask(mods)
        
        # Tell X we want to hear about it when this key is pressed...
        try:
            self.grab_key(keycode, modmask)
            self.register_hotkey(keycode, modmask, callback, user_data)
            return True
        except Exception as e:
            print e
            return False

    #
    # Keeps a mapping of keys to tiling actions
    #
    _DISPATCHER = {}
    
    _User_Data = {}
        
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
    # Mod2Mask (Number lock)
    # LockMask (Caps lock)
    # Mod2Mask | LockMask (Number lock and Caps lock)
    #
    # What about scroll lock? o_O
    #
    def grab_key(self, keycode, mask):
        Workarea.get_root().grab_key(keycode, mask, 1, X.GrabModeAsync, X.GrabModeAsync)
        Workarea.get_root().grab_key(keycode, mask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
        Workarea.get_root().grab_key(keycode, mask | X.LockMask, 1, X.GrabModeAsync, X.GrabModeAsync)
        Workarea.get_root().grab_key(keycode, mask | X.Mod2Mask | X.LockMask, 1, X.GrabModeAsync, X.GrabModeAsync)
        
    #
    # Simply ties a key code to a callback method in the Tile class. Valid key codes
    # can be found in the documentation provided. (But are based on the key symbols
    # defined in Xlib. Probably in Xlib/keysymdef/latin1.py and Xlib/keysymdef/miscellany.py)
    #
    @staticmethod
    def register_hotkey(keycode, mask, callback, user_data = None):
        if not keycode in XlibKeybinder._DISPATCHER:
            XlibKeybinder._DISPATCHER[keycode] = {}
        XlibKeybinder._DISPATCHER[keycode][mask] = callback
        if user_data:
            XlibKeybinder._User_Data[callback] = user_data 
        
        
        #
    # Initiate the dispatching routing.
    #
    # Has two contexts: Called with an action and called without.
    #
    # *Called with an action*
    # Implies that PyTyle is forcing the issue and wants something done. This also
    # means that we are here _not_ because of a key press. However, we still check
    # to see if tiling is enabled for this screen. If it isn't, we die.
    #
    # *Called without an action*
    # Implies that we have initiated the dispatch routine with a key press.
    # Therefore, we should check the currently pressed key, and follow the key
    # binding to run its respective method. Make sure to fail if tiling isn't
    # enabled and we aren't calling tile. (Essentially, pressing the tile key
    # binding is the only way to enable tiling.)
    #
    @staticmethod
    def dispatch(keycode, masks):
        if keycode not in XlibKeybinder._DISPATCHER:
                print >> sys.stderr, "Keycode %s is not bound" % keycode
                return
            
        # Now we need to determine which masks were used...
        if masks in XlibKeybinder._DISPATCHER[keycode]:
            callback = XlibKeybinder._DISPATCHER[keycode][masks]
        else:
            print >> sys.stderr, "Keycode %s and keymask %d are not bound" % (keycode, masks)
            return
        
        print callback
        if callback in XlibKeybinder._User_Data:
            callback(XlibKeybinder._User_Data[callback])
        else:
            callback()    
    
        