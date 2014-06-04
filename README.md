# Azulejo

Azulejo was originally a port (an attempt to) of [winsplit revolution](http://www.winsplit-revolution.com/)'s functionality to *nix desktop environments. This fork also adds Compiz's Put feature to the functionality.
Short: it moves, with or without resizing, windows using keyboard shortcuts.

It has been tested on gnome2, xfce and openbox, but it should work on many other desktop environments.

## Rationale

Traditional floating window managers are very intuitive and extremely popular. Most of the people don't even know other kinds of window managers exist, or what a window manager is.  
Being able to move and resize windows with a mouse is a killer feature, but for those that spend the whole day in front of a screen switching between windows and resize them every now and then, floating window managers end up standing more on the way than being helpful.  
Moving the hands back and forward between the keyboard and the mouse consumes too much time and is rather inefficient. Also, the mouse is not really designed to be a precision device, hitting the right pixel can be an headache.  
To mitigate these problems, some users switch to tiling window managers, which take a radically different approach and tend to be notoriously more productive. But the switch is often painful, many acquired workflows are abruptly broken and a fairly big amount of keyboard shortcuts need to be memorized just to achieve basic usage.  
This is where Azulejo comes in, it adds some tiling features but leaves your window manager untouched, you can still move and resize your windows with the mouse like you always did.

## Installation

Required Packages:

* Gtk3
* gir1.2-keybinder-3.0
* python-xlib
* python-notify2

Simply run the ''run.py'' file present on the project's root dir.


## Usage

Azulejo doesn't have a GUI nor a CLI, simply use the keyboard shortcuts, whenever you need.
Azulejo comes with two default keymaps. One uses the numpad (keypad), the other not. In the following, "KP" stands for keypad:

	Super+C		Switch the keymap

### Tile

	Super+2		Place two windows side by side
	Super+3		Place a window on the left half of the screen and two on the right half
	Super+4		Arrange four windows two by two
	Super+R		Rotate windows' positions i.e. cycle windows

### Move
	Super+KP 1	Move current window to left lower corner
	(or Super+J)	
	Super+KP 2	Move current window to bottom of the screen
	(or Super+K)
	Super+KP 3	Move current window to right lower corner
	(or Super+L)
	Super+KP 4	Move current window to the left
	(or Super+U)
	Super+KP 5	Move current window to center of the screen
	(or Super+I)
	Super+KP 6	Move current window to the right
	(or Super+O)
	Super+KP 7	Move current window to left upper corner
	(or Super+7)
	Super+KP 8	Move current window to top of the screen
	(or Super+8)
	Super+KP 9	Move current window to right upper corner
	(or Super+9)

### Move and Resize
	Super+Alt+KP 1	Resize and move current window to left lower corner
	(or Super+Alt+J)
	Super+Alt+KP 2	Resize and move current window to bottom of the screen
	(or Super+Alt+K)
	Super+Alt+KP 3	Resize and move current window to right lower corner
	(or Super+Alt+L)
	Super+Alt+KP 4	Resize and move current window to the left
	(or Super+Alt+U)
	Super+Alt+KP 5	Resize and move current window to center of the screen
	(or Super+Alt+I)
	Super+Alt+KP 6	Resize and move current window to the right
	(or Super+Alt+O)
	Super+Alt+KP 7	Resize and move current window to left upper corner
	(or Super+Alt+7)
	Super+Alt+KP 8	Resize and move current window to top of the screen
	(or Super+Alt+8)
	Super+Alt+KP 9	Resize and move current window to right upper corner
	(or Super+Alt+9)	
	
## Configuration

Azulejo configurations are stored on ''~/.azulejo/config.js''.
The keymaps are stored in ''~/.azulejo/Shortcuts''

TODO: add/explain example

## Author

Gilles   
email: ipfh42 at yahoo d0t de

### Author of the original project

Pedro   
[HTTP://lame hacks.net](http://lamehacks.net)   
email: Pedro at lame hacks d0t net
