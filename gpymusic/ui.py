from urwid import *
import logging

def exit_on_q(input):
   if input in ('q', 'Q'):
       raise urwid.ExitMainLoop()

def handle_command_noop(command):
    return True

handle_command = handle_command_noop


class UserInput(Edit):
    def __init__(self, *args, **kwargs):
        super(UserInput, self).__init__(*args, **kwargs)
        self.handler = self.default_handler
    def keypress(self, size, key):
        if key != 'enter':
            return super(UserInput, self).keypress(size, key)

        text = self.edit_text
        self.edit_text = ""
        logging.info("GPY command: %s" % text)
        self.handler(text)

    def default_handler(self, input):
        logging.info("GPY unhandled %s" % input)
        return True


class MainFrame(Frame):
    def __init__(self, body=None, footer=None, *args, **kwargs):

        self.main = Filler(Text('Loading..'), 'top')

        self.player = Text("Not playing anything now")

        self.queue = Frame(body=Filler(Text(" -- Empty queue --"), 'top'), header=Text("Queue songs"), footer=self.player)
        self.queuebox = LineBox(self.queue, title="Songs Queue", bline='')
                

        self.userInput = UserInput(caption="> ")
        self.statusBar = Text("Waiting for input, type ? for help")

        self.splitView = Columns([self.main, self.queuebox])


        footer = LineBox(
                Pile([self.statusBar, self.userInput]),
                lline='',
                rline='',
                bline='',
                tlcorner='',
                trcorner=''
                )

        super(MainFrame, self).__init__(body=self.splitView, footer=footer, focus_part='footer', *args, **kwargs)

    def test(self):
        logging.info("Here")
        widget = self.draw_table([])
        columns = self.splitView.contents
        columns[0] = Filler(Text('whaa'))


    def set_main(self, value):
        widget = None
        typeof = type(value)
        if typeof is str:
            widget = Text(value)
            self.main.original_widget = widget
        elif typeof is list:
            widget = self.draw_table(value)
            self.main.original_widget = widget



    def draw_table(self, list):
        """
            Draws a table out of a list of lists
            the first element on the list defined the max amount
            of columns. Assumes each cell contains a string
        """

        list = [
                ["this", "is", "a", "test1"],
                ["this", "is", "a", "test2"],
                ["this", "is", "a", "test3"]
               ]

        maxcells = len(list[0])
        cellrange = range(maxcells)
        table = []
        test = []
        for row in list:
            columns = []
            for cell in cellrange:
                if cell in row:
                    test.append(Text(row[cell]))
                    columns.append(Text(row[cell]))
                else:
                    columns.append(Text(''))
            table.append(Columns(columns))

        return ListBox(table)



    def set_input_handler(self, callback):
        self.userInput.handler = callback
