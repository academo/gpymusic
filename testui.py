import urwid
from urwid import *

loop = urwid.MainLoop(MainFrame(), unhandled_input=exit_on_q)
loop.run()
