"""xwin.py W H : resizes the mapped top-level game window on :98 and moves it to 0,0"""
import sys
from Xlib import display
d = display.Display(':98'); root = d.screen().root
for c in root.query_tree().children:
    if c.get_attributes().map_state == 2 and c.get_geometry().width > 300:
        c.configure(x=0, y=0, width=int(sys.argv[1]), height=int(sys.argv[2]))
        print('resized', hex(c.id))
d.sync()
