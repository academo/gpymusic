from urwid import *

def exit_on_q(input):
   if input in ('q', 'Q'):
       raise urwid.ExitMainLoop()


class MainFrame(Frame):
    def __init__(self, body=None, footer=None, *args, **kwargs):

        self.main = Filler(Text("Welcome to GPYMusic"), 'top')

        self.player = Text("Not playing anything now")

        self.queue = Frame(body=Filler(Text(" -- Empty queue --"), 'top'), header=Text("Queue songs"), footer=self.player)

        self.userInput = Edit("> ")
        self.statusBar = Text("Waiting for input")

        self.splitView = Columns([self.main, self.queue])

        super(MainFrame, self).__init__(body=self.splitView, footer=Pile([self.statusBar, self.userInput]), focus_part='footer', *args, **kwargs)

