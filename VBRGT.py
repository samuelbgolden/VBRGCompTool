from tkinter import Tk, TclError
from Positionals import *
from Database import *
from IOHandler import IOHandler


# its everything
class Application(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent  # establishes parent path
        self.parent.title('New Competition')  # the text at the bar at the top of the window

        self.config(bg=LBLUE)  # the background for the frame containing the whole application

        self.databaseHandler = DatabaseHandler(self)
        self.ioHandler = IOHandler(self, self.databaseHandler)  # object that handles csv stuff

        self.menubar = MenuBar(self, self.databaseHandler, self.ioHandler)  # declares 'File...' bar
        self.standingsTab = StandingsTab(self, self.databaseHandler, bg='red')  # right most tab containing competitor rankings
        self.entryTab = EntryTab(self, self.databaseHandler)  # center tab containing all info about one competitor
        self.competitorTab = CompetitorTab(self, self.databaseHandler)  # left most tab containing list of all competitors
        self.quickCommand = QuickCommand(self, self.databaseHandler)  # bottom bar that allows text based usage
        self.parent.configure(menu=self.menubar)  # declares menu to be the declared menubar object

        self.handle_fonts(self)

        self.quickCommand.pack(side='bottom', anchor=S, fill='x')
        self.competitorTab.pack(side='left', anchor=W, fill='y')  # packs as left-most
        self.entryTab.pack(side='left', anchor=W, fill='y')  # packs as second from left
        self.standingsTab.pack(side='left', anchor=W, fill='y')  # packs as third from left

        self.parent.protocol('WM_DELETE_WINDOW', self.ioHandler.close)  # handles clicking 'X' button with .close func

    def handle_fonts(self, obj):
        for widget in obj.winfo_children():
            self.handle_fonts(widget)
            try:
                widget.configure(font=general)
            except TclError:
                print('tclError')


    def update_all(self):  # app method where things that need to be updated whenever some data manip occurs
        self.standingsTab.update_all()  # updates every standings table
        self.competitorTab.competitorFrame.competitorTable.update_table()  # updates competitor list
        if self.entryTab.active():
            self.entryTab.competitorInfoFrame.fill_competitor(self.entryTab.competitorInfoFrame.idValue.get())
            self.entryTab.competitorInfoFrame.update_to_route_buttons()


# even more everything
if __name__ == '__main__':  # checks if full code is being run, rather than being imported as a module
    root = Tk()  # base tkinter object
    app = Application(root)
    app.pack(expand=1, fill='both')  # declares full app
    root.after(0, app.databaseHandler.update_main())  # this statements queues the update_main function, which contains
                                                      # the same statement, queuing the update_main function. this
                                                      # allows the update_main func to be called repeatedly,
                                                      # simultaneous with the tkinter event loop. the update_main func
                                                      # has an initial check to see if it is time to do an update, which
                                                      # is based on a flag set in another thread. it is this multi-
                                                      # threading that necessitates this event-queuing.
    root.mainloop()  # runs tkinter action loop
