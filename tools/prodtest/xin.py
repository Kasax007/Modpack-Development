"""Tiny X input helper over XTEST (Xvfb :98). usage: xin.py move X Y | click [BUTTON] | key NAME [NAME...] | type TEXT"""
import sys, time
from Xlib import X, XK, display
from Xlib.ext import xtest
d = display.Display(':98')
def key(name):
    code = d.keysym_to_keycode(XK.string_to_keysym(name))
    xtest.fake_input(d, X.KeyPress, code); d.sync(); time.sleep(0.08)
    xtest.fake_input(d, X.KeyRelease, code); d.sync(); time.sleep(0.15)
cmd = sys.argv[1]
if cmd == 'move':
    xtest.fake_input(d, X.MotionNotify, x=int(sys.argv[2]), y=int(sys.argv[3])); d.sync()
elif cmd == 'click':
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    xtest.fake_input(d, X.ButtonPress, b); d.sync(); time.sleep(0.08); xtest.fake_input(d, X.ButtonRelease, b); d.sync()
elif cmd == 'key':
    for n in sys.argv[2:]: key(n)
elif cmd == 'type':
    for ch in sys.argv[2]: key('space' if ch == ' ' else ch)
