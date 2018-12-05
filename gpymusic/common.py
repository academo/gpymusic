from gmusicapi import Mobileclient
import urwid
import logging
# Imports are stupid.
mc = Mobileclient(debug_logging=False)  # noqa Our interface to Google Play Music.

from . import nowplaying
from . import songqueue
from . import view
from . import writer
from . import ui

from os.path import expanduser, join


# Location where we keep songs, playlists, libraries, and source code.
DATA_DIR = join(expanduser('~'), '.local', 'share', 'gpymusic')
# Location where we keep user and mpv configurations.
CONFIG_DIR = join(expanduser('~'), '.config', 'gpymusic')

q = songqueue.Queue()  # Queue/playlist.
w = writer.Writer(None, None, None, None, curses=False)  # Output handler.
v = view.View()  # Main window contents.
np = nowplaying.NowPlaying()
view = ui.MainFrame()
client = None  # To be set in the main executable.
loop = urwid.MainLoop(view, unhandled_input=ui.exit_on_q)

def start_ui():
    loop.run()
