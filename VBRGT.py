from tkinter import Tk, TclError
from Positionals import *
from Database import *
from IOHandler import *


class Application(Frame):
    def __init__(self, parent, user=None, password=None, address=None, database=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent  # establishes parent path
        self.parent.title('New Competition')  # the text at the bar at the top of the window

        self.config(bg=LBLUE)  # the background for the frame containing the whole application

        self.SCREEN_HEIGHT = self.parent.winfo_screenheight()
        self.SCREEN_WIDTH = self.parent.winfo_screenwidth()

        if user and password and address and database:
            self.databaseHandler = GlobalDatabase(self, user=user, password=password, address=address, database=database)
        else:
            self.databaseHandler = LocalDatabase(self)

        self.ioHandler = IOHandler(self, self.databaseHandler)  # object that handles csv stuff

        self.menubar = MenuBar(self, self.databaseHandler, self.ioHandler)  # declares 'File...' bar
        self.standingsTab = StandingsTab(self, self.databaseHandler, bg='red')  # right most tab containing competitor rankings
        self.entryTab = EntryTab(self, self.databaseHandler)  # center tab containing all info about one competitor
        self.competitorTab = CompetitorTab(self, self.databaseHandler)  # left most tab containing list of all competitors
        self.quickCommand = QuickCommand(self, self.databaseHandler)  # bottom bar that allows text based usage
        self.parent.configure(menu=self.menubar)  # declares menu to be the declared menubar object

        self.competitorTab.grid(row=0, column=0, sticky='nsew')
        self.entryTab.grid(row=0, column=1, sticky='nsew')
        self.standingsTab.grid(row=0, column=2, sticky='nsew')
        self.quickCommand.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.rowconfigure(0, weight=15)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)

        self.parent.protocol('WM_DELETE_WINDOW', self.ioHandler.close)  # handles clicking 'X' button with .close func

    def update_all(self):  # app method where things that need to be updated whenever some data manip occurs
        self.standingsTab.update_all()  # updates every standings table
        compframe = self.competitorTab.competitorFrame
        compframe.competitorTable.update_table(compframe.competitorSearchBar.content.get())  # updates competitor list


########################################################################################################################


class SessionPrompt(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.parent = parent

        self.parent.resizable(False, False)

        self.hostVar = BooleanVar()
        self.hostVar.set(False)
        self.connectToDB = BooleanVar()
        self.connectToDB.set(False)

        self.parent.title('Before you begin...')

        self.applicationTitle = Label(self, text='Competitions at VBRG')
        self.modeLabel = Label(self, text='What mode will you use for this session?')
        self.singleButton = Radiobutton(self, text='Single Computer', variable=self.connectToDB, value=False,
                                        command=self.change_gridded_frame)
        self.multipleButton = Radiobutton(self, text='Multiple Computers', variable=self.connectToDB, value=True,
                                          command=self.change_gridded_frame)
        self.applicationTitle.grid(row=0, column=0, columnspan=4, sticky='nsew')
        self.modeLabel.grid(row=1, column=0, columnspan=4, sticky='w')
        self.singleButton.grid(row=2, column=0, columnspan=2, sticky='nsew')
        self.multipleButton.grid(row=2, column=2, columnspan=2, sticky='nsew')

        self.singleFrame = Frame(self)
        self.newButton = Button(self.singleFrame, text='Begin a new competition', relief='flat', command=self.new_competition)
        self.existingButton = Button(self.singleFrame, text='Open an existing competition', relief='flat', command=self.open_competition)
        self.singleFrame.grid(row=3, column=0, columnspan=4, sticky='nsew')
        self.newButton.grid(row=0, column=0, sticky='nsew')
        self.existingButton.grid(row=1, column=0, sticky='nsew')

        self.multipleFrame = Frame(self)
        self.userLabel = Label(self.multipleFrame, text='Database user:')
        self.passwordLabel = Label(self.multipleFrame, text='Database user password:')
        self.addressLabel = Label(self.multipleFrame, text='Host machine address:')
        self.databaseLabel = Label(self.multipleFrame, text='Database name:')
        self.userEntry = Entry(self.multipleFrame)
        self.passwordEntry = Entry(self.multipleFrame)
        self.addressEntry = Entry(self.multipleFrame)
        self.databaseEntry = Entry(self.multipleFrame)
        self.hostCheckbox = Checkbutton(self.multipleFrame, text='This is the host machine', variable=self.hostVar,
                                        command=self.affect_address_state, onvalue=True, offvalue=False)
        self.goButton = Button(self.multipleFrame, text='Go', command=self.connect_to_global)
        self.multipleFrame.grid(row=3, column=0, columnspan=4, sticky='nsew')
        self.userLabel.grid(row=0, column=0, sticky='w')
        self.userEntry.grid(row=0, column=1)
        self.passwordLabel.grid(row=1, column=0, sticky='w')
        self.passwordEntry.grid(row=1, column=1)
        self.hostCheckbox.grid(row=2, column=0, columnspan=2, sticky='w')
        self.addressLabel.grid(row=3, column=0, sticky='w')
        self.addressEntry.grid(row=3, column=1)
        self.databaseLabel.grid(row=4, column=0, sticky='w')
        self.databaseEntry.grid(row=4, column=1)
        self.goButton.grid(row=5, column=0, columnspan=2, sticky='nsew')

        self.multipleFrame.grid_remove()
        self.userEntry.bind('<Return>', self.connect_to_global)
        self.passwordEntry.bind('<Return>', self.connect_to_global)
        self.hostCheckbox.bind('<Return>', self.connect_to_global)
        self.addressEntry.bind('<Return>', self.connect_to_global)
        self.databaseEntry.bind('<Return>', self.connect_to_global)

    def affect_address_state(self):
        if self.hostVar.get():
            self.addressEntry.config(state='disable')
            self.addressLabel.config(state='disable')
        else:
            self.addressEntry.config(state='normal')
            self.addressLabel.config(state='normal')

    def change_gridded_frame(self):
        if self.connectToDB.get():
            self.singleFrame.grid_remove()
            self.multipleFrame.grid()
        else:
            self.multipleFrame.grid_remove()
            self.singleFrame.grid()

    def new_competition(self):
        app = Application(self.parent)
        self.change_root_settings(app)

    def open_competition(self):
        app = Application(self.parent)
        app.ioHandler.open()
        self.change_root_settings(app)

    def connect_to_global(self, *args):
        user = self.userEntry.get()
        password = self.passwordEntry.get()
        if self.hostVar.get():
            address = 'localhost'
        else:
            address = self.addressEntry.get()
        database = self.databaseEntry.get()
        app = Application(self.parent, user=user, password=password, address=address, database=database)
        self.change_root_settings(app)
        self.parent.after(0, app.databaseHandler.update_main())
        # this statements queues the update_main function, which contains the same statement, queuing the update_main
        # function. this allows the update_main func to be called repeatedly, simultaneous with the tkinter event loop.
        # the update_main func has an initial check to see if it is time to do an update, which is based on a flag set
        # in another thread. it is this multi-threading that necessitates this event-queuing.

    def change_root_settings(self, app):
        self.grid_remove()
        self.parent.resizable(True, True)
        app.grid(column=0, row=0, sticky='nsew')


if __name__ == '__main__':  # checks if full code is being run, rather than being imported as a module
    root = Tk()  # base tkinter object
    options = SessionPrompt(root)
    options.grid(row=0, column=0, sticky='nsew')
#    app = Application(root)
#    app.grid(row=0, column=0, sticky='nsew')  # declares full app
#    root.after(0, app.databaseHandler.update_main())

    root.mainloop()  # runs tkinter action loop
