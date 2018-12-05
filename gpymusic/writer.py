from urwid import *

from . import common

from time import sleep

import curses as crs
import sys

import logging

class Writer():

    def __init__(
            self, main, inbar, infobar, outbar,
            curses=True, urwid=True, colour=False, test=False):
        """
        Writer constructor.

        Arguments:
        main/inbar/infobar/outbar: curses windows.

        Keyword arguments:
        curses=True: Flag for disabling curses output.
        colour=False: Flag for disabling colour output.
        test=False: Flag to disable all output for unit testing.
          If test is True, then curses must be disabled.
        """
        if test and curses:
            print('Incompatible arguments to writer: '
                  'curses must be disabled to test.')
            sleep(1)
            exit(1)

        self.main = main
        self.inbar = inbar
        self.infobar = infobar
        self.outbar = outbar
        self.curses = curses
        self.urwid = urwid
        self.colour = colour
        self.test = test
        self.xlimit = self.main.getmaxyx()[1] if main is not None else 0
        self.ylimit = self.main.getmaxyx()[0] if main is not None else 0

    @staticmethod
    def trunc(string, ch):
        """
        Pads a string with '...' if it is too long to fit in a window.

        Arguments:
        string: String to be truncated.
        ch: Max length for the string.

        Returns: The original string if it is short enough to  displayed,
          otherwise the string truncated and padded with '...'.
        """

        if ch < 0 or len(string) <= ch:
            return string
        else:
            return string[:-((len(string) - ch) + 3)] + '...'

    def replace_windows(self, main, inbar, infobar, outbar):
        self.main = main
        self.inbar = inbar
        self.infobar = infobar
        self.outbar = outbar
        self.ylimit = self.main.getmaxyx()[0]
        self.xlimit = self.main.getmaxyx()[1]

    def addstr(self, win, string):
        """
        Replace the contents of a window with a new string.
          Not for anything where position matters.

        Arguments:
        win: Window on which to display the string.
        string: String to be displayed.
        """
        if not self.curses:
            if not self.test:
                print(string)
            return

        win.erase()
        win.addstr(Writer.trunc(string, self.xlimit - 1))
        win.refresh()

    def refresh(self):
        """Refresh all windows."""
        if not self.curses:
            return

        self.main.refresh()
        self.inbar.refresh()
        self.infobar.refresh()
        self.outbar.refresh()

    def now_playing(self, string=None):
        """
        Show 'now playing' information. If both kwargs are None,
          nothing is playing.

        Keyword arguments:
        string=None: Formatted song string.
        """
        if self.test:
            return
        # common.np.update(string if string is not None else '')
        # self.addstr(self.infobar, 'Now playing: %s' %
                    # (string if string is not None else 'None'))

    def erase_outbar(self):
        """Erases content on the outbar."""
        if not self.curses or not self.urwid:
            return

        self.outbar_msg('')

    def error_msg(self, msg):
        """
        Displays an error message.

        Arguments:
        win: Window on which to display the message.
        msg: Message to be displayed.
        """
        if self.test:
            return

        self.outbar_msg('Error: %s. Enter \'h\' or \'help\' for help.' % msg)

    def welcome(self):
        """Displays a welcome message."""

        if not self.urwid:
            if not self.test:
                print('Welcome to Google Py Music!')
            return

        common.view.set_main('Welcome to Google Py Music!\n\nType "?" for help')

    def goodbye(self, msg=''):
        """
        Exit gpymusic.

        Arguements:
        msg='': Message to display prior to exiting.
        """
        if not self.curses:
            if not self.test:
                print(msg)
            sys.exit()

        self.addstr(self.outbar, msg)
        common.mc.logout()
        try:
            common.client.mm.logout()
        except:
            pass
        sleep(2)
        crs.curs_set(1)
        crs.endwin()
        sys.exit()

    def get_input(self):
        """
        Get user input in the bottom bar.

        Returns: The user-inputted string.
        """
        if not self.curses:
            return input('Enter some input: ')

        self.addstr(self.inbar, '> ')
        crs.curs_set(2)  # Show the cursor.

        try:
            string = self.inbar.getstr()
        except KeyboardInterrupt:
            common.np.close()
            self.goodbye('Goodbye, thanks for using Google Py Music!')

        self.inbar.deleteln()
        crs.curs_set(0)  # Hide the cursor.

        return string.decode('utf-8')

    def outbar_msg(self, msg):
        """
        Display a basic output message.

        Arguments:
        msg: Message to be displayed.
        """
        if self.test:
            return
        common.view.statusBar.set_text(msg)

    def measure_fields(self, width):
        """
        Determine max number of characters and starting point
          for category fields.

        Arguments:
        width: Width of the window being divided.

        Returns: A tuple containing character allocations
          and start positions.
        """
        padding = 1  # Space between fields.
        i_ch = 3  # Characters to allocate for index.
        # Width of each name, artist, and album fields.
        n_ch = ar_ch = al_ch = int((width - i_ch - 3 * padding) / 3)
        al_ch -= 1  # Hacky guard against overflow.

        total = sum([i_ch, n_ch, ar_ch, al_ch, 3 * padding])

        if total != width:  # Allocate any leftover space to name.
            n_ch += width - total

        # Field starting x positions.
        n_start = 0 + i_ch + padding
        ar_start = n_start + n_ch + padding
        al_start = ar_start + ar_ch + padding

        return (i_ch, n_ch, ar_ch, al_ch,
                n_start, ar_start, al_start)

    def display(self):
        """Update the main window with some content."""
        if common.v.is_empty():
            return

        c = common.v  # Content to display.

        if not self.curses and not self.urwid:
            if not self.test:
                i = 1
                if 'songs' in c and c['songs']:
                    print('Songs:')
                for song in c['songs']:
                    print('%d: %s' % (i, str(song)))
                    i += 1
                if 'artists' in c and c['artists']:
                    print('Artists:')
                for artist in c['artists']:
                    print('%d: %s' % (i, str(artist)))
                    i += 1
                if 'albums' in c and c['albums']:
                    print('Albums:')
                for album in c['albums']:
                    print('%d: %s' % (i, str(album)))
                    i += 1
            return

        # This list will be rendered by the UI
        list = []

        # Song index
        i = 1

        # Songs header.
        if 'songs' in c and c['songs']:
            list.append(["#", "Title", "Artist", "Album"])

            # Write each song.
            for song in c['songs']:
                item = []
                
                if song['kind'] == 'song':
                    item = [
                            # Number
                            str(i),
                            song['name'],
                            song['artist']['name'],
                            song['album']['name']
                           ]
                else:
                    item = [
                            # Number
                            str(i),
                            song['name'],
                            song['artist'],
                            song['album']
                           ]
                list.append(item)
                i += 1

        # Artists header.
        if 'artists' in c and c['artists']:
            list.append(["#", "Artist"])

            # Write each artist.
            for artist in c['artists']:
                item = [
                        # Number
                        str(i),
                        artist['name']
                       ]
                list.append(item)
                i += 1

        # Albums header.
        if 'albums' in c and c['albums']:
            list.append(["#", "Album", "Artist"])

            # Write each album.
            for album in c['albums']:
                item = [
                        # Number
                        str(i),
                        album['name'],
                        album['artist']['name']
                       ]
                list.append(item)
                i += 1

        common.view.set_main(list)
