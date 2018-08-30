from tkinter import Menu, Radiobutton, Spinbox, W, N, E, S, Scrollbar, LEFT, Grid, TOP, Listbox
from Interactives import *


# the gray bar that contains 'File' and the associated commands
# child of Application
class MenuBar(Menu):
    def __init__(self, parent, db, io, *args, **kwargs):
        Menu.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db
        self.io = io

        self.config(background=LBLUE)

        self.filemenu = Menu(self, tearoff=0)  # creates 'File' cascade
        self.filemenu.add_command(label="New Competition", command=self.io.new)  # each 'add_command' call creates a new
        self.filemenu.add_command(label="Save", command=self.io.save)            # selectable item for a cascade menu.
        self.filemenu.add_command(label="Save as...", command=self.io.save_as)   # the 'command' argument is the func
        self.filemenu.add_separator()                                            # that will be called when the item
        self.filemenu.add_command(label="Open", command=self.io.open)            # is clicked on. the 'add_separator'
        self.filemenu.add_command(label="Export")                                # func adds a thin black bar between
        self.filemenu.add_command(label="Print")                                 # grouped items in the cascade
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close", command=self.io.close)

        self.networkmenu = Menu(self, tearoff=0)  # creates 'Network' cascade
       # self.networkmenu.add_command(label="Connect to database", command=self.db.connect)
       # self.networkmenu.add_command(label="Configure database connection", command=self.db.prompt)
       # self.networkmenu.add_command(label="Insert competition in global database", command=self.db.open_to_global)
       # self.networkmenu.add_command(label="Refresh from database", command=self.gdb.pull)

        self.add_cascade(label="File", menu=self.filemenu, background=LBLUE)  # adds 'File' and 'Network' cascades to
        self.add_cascade(label="Network", menu=self.networkmenu)              # menubar itself.


########################################################################################################################


# a full tab frame, containing name buttons and routes
# child of Application
class EntryTab(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.config(bg=LBLUE)

        self.routeAttemptsEntryFrame = RouteAttemptsEntryFrame(self, self.db, bg=LBLUE)  # creates frame for route btns
        self.competitorInfoFrame = CompetitorInfoFrame(self, self.db, bg=LBLUE)  # creates frame for individual info

        self.competitorInfoFrame.pack(side=TOP, anchor=N + W, padx=10)  # packs 1st from top
        self.routeAttemptsEntryFrame.pack(side=TOP, fill='y', anchor='center', padx=20, pady=10, expand=1)  # packs 2nd from top

        self.bind('<FocusIn>', self.foc_in)  # when this widget gains focus, the 'foc_in' func is called

    def active(self):
        return self.competitorInfoFrame.idValue.get() != 0

    def foc_in(self, *args):  #
        if self.competitorInfoFrame.idValue.get() == 0:  # checks if the id of competitor has changed from default value
            disable_frame(self.competitorInfoFrame)  # disables competitorInfoFrame
            disable_frame(self.routeAttemptsEntryFrame)  # disables routeAttemptsEntryFrame


# a frame that will display the buttons which can select attempts needed to finish up to 5 routes
# child of EntryTab
class RouteAttemptsEntryFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.routes = [RouteAttemptsEntry(self, x, bg=LBLUE) for x in range(1, 51)]  # creates sets of buttons for route
                                                                                     # attempts and completion entry
        for i, route in enumerate(self.routes):  # iterating through routes created above
            if i < 25:                             # this if else creates the two columns of RouteAttemptsEntry
                route.grid(row=i % 25, column=0, stick='nsew')   # objects by sorting by id (less than 25 and greater or equal to 25),
            else:                                  # and griding them on different columns according to those
                route.grid(row=i % 25, column=2, stick='nsew')   # categories
        Frame(self, width=2, bg=DDBLUE).grid(row=0, rowspan=25, column=1, stick='nsew', padx=10)  # vertical rule
        for i in range(0, 25):
            self.rowconfigure(i, weight=1)  # sets expand weight for all Grid rows

    def get_selected_routes(self):
        selected = []
        for route in self.routes: # iterates through all the RouteAttemptsEntry objects
            if route.isActive:  # checks if the route is activated
                selected.append(route)  # adds that route to the 'selected' list
        return selected  # returns selected routes

    def update_from_info_entries(self, values):  # should be 10 values (5 route #s and 5 attempt amounts; in that order)
        self.reset()  # clears the activated RouteAttemptsEntry button sets
        for i in range(0, 5):  # iterates through
            if not(values[i] == 0):  # if a number is zero, it isn't handled
                self.routes[values[i] - 1].activate()  # otherwise activate the route and
                self.routes[values[i] - 1].attemptsAmt.set(values[i+5])  # set its attempts to the appropriate amount

    def reset(self):  # clears all activated routes
        for route in self.routes:  #
            route.attemptsAmt.set(0)
            route.deactivate()

    def not_five_routes_selected(self):
        count = 0
        for route in self.routes:
            if route.isActive:  # checks if route is selected
                count += 1
        if count < 5:
            return True
        return False


# a frame that will display the full editable information for any given competitor
# child of EntryTab
class CompetitorInfoFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.labelbg = LBLUE
        self.labelfg = 'white'
        self.entrybg = LLBLUE
        self.entryfg = 'black'
        self.entrydisabledbg = LBLUE

        self.sexValue = StringVar()
        self.idValue = IntVar()
        self.levelValues = ('Beginner', 'Intermediate', 'Advanced', 'Open')
        self.routeValues = [StringVar()]

        self.routeListingFrame = Frame(self, bg=self.labelbg)

        self.idValueLabel = Label(self, textvariable=self.idValue, bg=self.labelbg, fg=self.labelfg)
        self.idLabel = Label(self, text='ID: ', bg=self.labelbg, fg=self.labelfg)
        self.frameTitleLabel = Label(self, text="COMPETITOR INFO", bg=self.labelbg, fg=self.labelfg)
        self.fnameLabel = Label(self, text='FIRST:', bg=self.labelbg, fg=self.labelfg)
        self.lnameLabel = Label(self, text='LAST:', bg=self.labelbg, fg=self.labelfg)
        self.levelLabel = Label(self, text='LEVEL:', bg=self.labelbg, fg=self.labelfg)
        self.sexLabel = Label(self, text='SEX:', bg=self.labelbg, fg=self.labelfg)
        self.ageLabel = Label(self, text='AGE:', bg=self.labelbg, fg=self.labelfg)
        self.routesLabel = Label(self.routeListingFrame, text='ROUTES:', bg=self.labelbg, fg=self.labelfg)
        self.attemptsLabel = Label(self.routeListingFrame, text='ATTEMPTS:', bg=self.labelbg, fg=self.labelfg)

        self.fnameEntry = Entry(self, width=30, fg=self.entryfg, bg=self.entrybg, disabledbackground=self.entrydisabledbg)
        self.lnameEntry = Entry(self, width=30, fg=self.entryfg, bg=self.entrybg, disabledbackground=self.entrydisabledbg)
        self.levelEntry = Spinbox(self, values=self.levelValues, width=28, fg=self.entryfg, bg=self.entrybg, disabledbackground=self.entrydisabledbg)
        self.sexEntryM = Radiobutton(self, text='M', variable=self.sexValue, value='M', fg=self.entryfg, bg=self.labelbg)
        self.sexEntryF = Radiobutton(self, text='F', variable=self.sexValue, value='F', fg=self.entryfg, bg=self.labelbg)
        self.ageEntry = Spinbox(self, from_=1, to=100, width=10, fg=self.entryfg, bg=self.entrybg, disabledbackground=self.entrydisabledbg)
        self.routeEntries = [Entry(self.routeListingFrame, width=3, fg=self.entryfg, bg=self.entrybg, disabledbackground=self.entrydisabledbg) for _ in range(5)]
        self.attemptEntries = [Entry(self.routeListingFrame, width=3, fg=self.entryfg, bg=self.entrybg, disabledbackground=self.entrydisabledbg) for _ in range(5)]

        self.updateButton = Button(self, text='Update Competitor', command=self.update_competitor, bg=DBLUE, fg='white')

        self.frameTitleLabel.grid(stick='ew', row=0, column=0, columnspan=6)
        self.idLabel.grid(stick='nw', row=1, column=0)
        self.idValueLabel.grid(stick='nw', row=1, column=1)
        self.fnameLabel.grid(stick='nw', row=2, column=0)
        self.fnameEntry.grid(stick='nw', row=2, column=1, columnspan=5)
        self.lnameLabel.grid(stick='nw', row=3, column=0)
        self.lnameEntry.grid(stick='nw', row=3, column=1, columnspan=5)
        self.levelLabel.grid(stick='nw', row=4, column=0)
        self.levelEntry.grid(stick='nw', row=4, column=1, columnspan=5)
        self.sexLabel.grid(stick='nw', row=5, column=0)
        self.sexEntryM.grid(stick='nw', row=5, column=1)
        self.sexEntryF.grid(stick='nw', row=5, column=2)
        Frame(self, height=20, width=2, bg='grey').grid(stick='nw', row=5, column=3)
        self.ageLabel.grid(stick='nw', row=5, column=4)
        self.ageEntry.grid(stick='nw', row=5, column=5)
        self.routeListingFrame.grid(stick='nw', row=7, column=0, columnspan=6)
        self.routesLabel.grid(stick='nsw', row=0, column=0)
        for i, entry in enumerate(self.routeEntries):
            Label(self.routeListingFrame, text=i+1, fg='white', bg=DDBLUE)\
                .grid(column=2*i+1, row=0, rowspan=2, stick='ns')
            entry.grid(stick='nw', row=0, column=2*i+2)
            entry.bind('<FocusOut>', self.update_to_route_buttons)
        self.attemptsLabel.grid(stick='nsw', row=1, column=0)
        for i, entry in enumerate(self.attemptEntries):
            entry.grid(stick='nw', row=1, column=2*i+2)
            entry.bind('<FocusOut>', self.update_to_route_buttons)
        self.updateButton.grid(row=8, column=0, columnspan=6)

        taborder = []
        for i in range(0, 5):
            taborder.append(self.routeEntries[i])
            taborder.append(self.attemptEntries[i])

        for widget in taborder:
            widget.lift()

        for i in range(0, Grid.grid_size(self)[0]):
            Grid.grid_rowconfigure(self, i, weight=1)
        for i in (0, Grid.grid_size(self)[0]):
            Grid.grid_columnconfigure(self, i, weight=1)
        for i in (0, Grid.grid_size(self.routeListingFrame)[0]):
            Grid.grid_rowconfigure(self.routeListingFrame, i, weight=1)
        for i in (0, Grid.grid_size(self.routeListingFrame)[0]):
            Grid.grid_columnconfigure(self.routeListingFrame, i, weight=1)

        disable_frame(self.parent)

    def fill_competitor(self, id):
        row = self.db.get_row(id)  # get_row
        self.clear_competitor()
        self.idValue.set(id)
        self.fnameEntry.insert(0, row[1])
        self.lnameEntry.insert(0, row[2])
        self.levelEntry.insert(0, row[3])
        self.sexValue.set(row[4])
        self.ageEntry.insert(0, row[5])
        # need score thing here for row[6]?
        for i in range(0, 5):
            if row[i+7] != 0:  # checks if is there a route in the database row
                self.routeEntries[i].insert(0, row[i+7])
                self.attemptEntries[i].insert(0, row[i+12])
                self.parent.routeAttemptsEntryFrame.routes[row[i+7] - 1].attemptsAmt.set(row[i+12])
                self.parent.routeAttemptsEntryFrame.routes[row[i+7] - 1].activate()

    def clear_competitor(self):
        self.idValue.set(0)
        self.fnameEntry.delete(0, 'end')
        self.lnameEntry.delete(0, 'end')
        self.levelEntry.delete(0, 'end')
        self.ageEntry.delete(0, 'end')
        for entry in self.routeEntries:
            entry.delete(0, 'end')
        for entry in self.attemptEntries:
            entry.delete(0, 'end')

    def validate_entries(self):
        for i in range(0, 5):
            if not(range(1, 51).__contains__(mk_int(self.routeEntries[i].get()))):
                self.routeEntries[i].delete(0, 'end')
                self.attemptEntries[i].delete(0, 'end')
            else:
                for widget in self.routeEntries[0:i]:
                    if widget.get() == self.routeEntries[i].get():
                        self.routeEntries[i].delete(0, 'end')
                        self.attemptEntries[i].delete(0, 'end')

            if not(range(1, 101).__contains__(mk_int(self.attemptEntries[i].get()))):
                # self.routeEntries[i].delete(0, 'end')
                self.attemptEntries[i].delete(0, 'end')

    def get_entered_values(self):
        self.validate_entries()
        entered = [0 for _ in range(0, 10)]  # Route id's take first five spots, attempts take next 5
        for i in range(0, 5):
            entered[i] = mk_int(self.routeEntries[i].get())
            entered[i+5] = mk_int(self.attemptEntries[i].get())
        return entered

    def update_to_route_buttons(self, *args):
        entered = self.get_entered_values()
        self.parent.routeAttemptsEntryFrame.update_from_info_entries(entered)

    def update_from_route_buttons(self):
        selected = self.parent.routeAttemptsEntryFrame.get_selected_routes()
        for i in range(0, 5):
            self.routeEntries[i].delete(0, 'end')
            self.attemptEntries[i].delete(0, 'end')
        for i, route in enumerate(selected):
            self.routeEntries[i].insert(0, route.num)
            self.attemptEntries[i].insert(0, route.attemptsAmt.get())

    def update_competitor(self):
        routevalues = []
        attemptvalues = []
        for entry in self.routeEntries:
            if entry.get() == '':
                routevalues.append(0)
            else:
                routevalues.append(entry.get())
        for entry in self.attemptEntries:
            if entry.get() == '':
                attemptvalues.append(0)
            else:
                attemptvalues.append(entry.get())  # these two for loops prevent passing empty strings to the database
        
        row = (self.fnameEntry.get(), self.lnameEntry.get(), self.levelEntry.get(), self.sexValue.get(),
               self.ageEntry.get(), self.calc_score(), routevalues[0], routevalues[1], routevalues[2],
               routevalues[3], routevalues[4], attemptvalues[0], attemptvalues[1], attemptvalues[2],
               attemptvalues[3], attemptvalues[4])
        self.db.update_row(self.idValue.get(), row)  # loads info to database
        self.clear_competitor()  # clears competitor info in entries
        self.parent.routeAttemptsEntryFrame.reset()  # resets route entries back to gray state with no values
        disable_frame(self)  # disables competitorInfoFrame
        disable_frame(self.parent.routeAttemptsEntryFrame)  # disables routeAttemptsEntryFrame
        self.parent.parent.competitorTab.competitorFrame.competitorSearchBar.clear()

    def calc_score(self):
        score = 0

        for entry in self.routeEntries:
            if entry.get() != '':
                score += int(entry.get()) * 100
            else:
                break
        return score


########################################################################################################################


# frame containing the CategoricalStandings objects
# child of Application
class StandingsTab(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.config(bg=DBLUE)

        self.title = Label(self, text='STANDINGS', bg=DBLUE, fg='white')
        self.title.grid(row=0, column=0, columnspan=2, stick=N)

        self.standings = self.create_standard_standings()
        for i, standing in enumerate(self.standings):
            standing.grid(row=(i % 4)+1, column=i//4, stick='ns')
            self.rowconfigure((i % 4)+1, weight=1)

    def create_standard_standings(self):
        levels = ('Beginner', 'Intermediate', 'Advanced', 'Open')
        genders = ('M', 'F')

        standings = []
        for g in genders:
            for l in levels:
                standings.append(CategoricalStandings(self, self.db, borderwidth=3, background='gray', level=l, sex=g))
        return standings

    def update_all(self):
        for standing in self.standings:
            standing.update_table()


# frame containing a single list of competitors by score for a specified set of attributes
# child of StandingsTab
class CategoricalStandings(Frame):
    def __init__(self, parent, db, level=None, sex=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.titlebg = LBLUE
        self.titlefg = 'black'

        self.selectedAttributes = {'level': level, 'sex': sex}
        self.titleString = StringVar()
        self.titleString.set('{} | {} ({})'.format(level, sex, 0))

        scrollbar = Scrollbar(self)
        scrollbar.config(command=self.set_scrollables)

        self.title = Label(self, textvariable=self.titleString, bg=self.titlebg, fg=self.titlefg)
        self.idLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=3, activestyle='none')
        self.fnameLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=10, activestyle='none')
        self.lnameLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=18, activestyle='none')
        self.scoreLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=10, activestyle='none')

        scrollbar.pack(side='right', fill='y', expand=True),
        self.title.pack(side='top', fill='x', expand=False)
        self.idLB.pack(side='left', fill='y', expand=True)
        self.fnameLB.pack(side='left', fill='y', expand=True)
        self.lnameLB.pack(side='left', fill='y', expand=True)
        self.scoreLB.pack(side='left', fill='y', expand=True)

        self.update_table()

    def set_scrollables(self, *args):
        self.idLB.yview(*args)
        self.fnameLB.yview(*args)
        self.lnameLB.yview(*args)
        self.scoreLB.yview(*args)

    def update_table(self):
        self.clear_table()
        rows = self.db.get_specific_rows_by_score(**self.selectedAttributes)
        if rows:
            self.titleString.set('{} | {} ({})'.format(self.selectedAttributes['level'],
                                                       self.selectedAttributes['sex'],
                                                       len(rows)))
            for i, row in enumerate(rows):
                self.idLB.insert(i, row[0])
                self.fnameLB.insert(i, row[1])
                self.lnameLB.insert(i, row[2])
                self.scoreLB.insert(i, row[3])
        else:
            self.titleString.set('{} | {} ({})'.format(self.selectedAttributes['level'],
                                                       self.selectedAttributes['sex'],
                                                       0))

    def clear_table(self):
        self.idLB.delete(0, 'end')
        self.fnameLB.delete(0, 'end')
        self.lnameLB.delete(0, 'end')
        self.scoreLB.delete(0, 'end')


########################################################################################################################


# frame containing the table of competitors, search bar, registration window creation
# child of Application
class CompetitorTab(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.competitorFrame = CompetitorFrame(self, self.db)
        self.competitorSelectionFrame = CompetitorSelectionFrame(self, self.db)

        self.competitorSelectionFrame.pack(side=LEFT, expand=1, fill='y')
        self.competitorFrame.pack(side=LEFT, expand=1, fill='y')


# frame containing the search bar and table of competitors
# child of CompetitorTab
class CompetitorFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.competitorSearchBar = CompetitorSearchBox(self)
        self.competitorTable = CompetitorTable(self, self.db, background=DBLUE)
        self.clearSearchButton = Button(self, text='CLEAR', background=BLUE, foreground='white', command=self.competitorSearchBar.clear)

        self.competitorSearchBar.grid(row=0, column=0, sticky='nsew')
        self.clearSearchButton.grid(row=0, column=1, sticky='e')
        self.competitorTable.grid(row=1, column=0, sticky='nsew', columnspan=2)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)


# frame that holds all the records of the competitors
# child of CompetitorFrame
class CompetitorTable(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.config(bg=LLBLUE)

        self.tablebg = 'white'
        self.tableborder = LLBLUE

        scrollbar = Scrollbar(self)
        self.idLB = Listbox(self, yscrollcommand=scrollbar.set, background=self.tablebg, highlightbackground=self.tableborder, borderwidth=0, width=6)
        self.fnameLB = Listbox(self, yscrollcommand=scrollbar.set, background=self.tablebg, highlightbackground=self.tableborder, borderwidth=0, width=25)
        self.lnameLB = Listbox(self, yscrollcommand=scrollbar.set, background=self.tablebg, highlightbackground=self.tableborder, borderwidth=0, width=25)
        self.levelLB = Listbox(self, yscrollcommand=scrollbar.set, background=self.tablebg, highlightbackground=self.tableborder, borderwidth=0, width=12)
        self.sexLB = Listbox(self, yscrollcommand=scrollbar.set, background=self.tablebg, highlightbackground=self.tableborder, borderwidth=0, width=2)
        self.ageLB = Listbox(self, yscrollcommand=scrollbar.set, background=self.tablebg, highlightbackground=self.tableborder, borderwidth=0, width=3)
        self.registerButton = Button(self, bg=BLUE, fg='white', text="REGISTER\nNEW",
                                     borderwidth=1, command=self.register_new)
        self.deleteButton = Button(self, bg=BLUE, fg='white', text="DELETE\nSELECTED",
                                   borderwidth=1, command=self.delete_competitor)
        self.editButton = Button(self, bg=BLUE, fg='white', text="EDIT\nSELECTED",
                                 borderwidth=1, command=self.edit_competitor)
        self.idLB.bind('<Delete>', self.delete_competitor)
        self.fnameLB.bind('<Delete>', self.delete_competitor)
        self.lnameLB.bind('<Delete>', self.delete_competitor)
        self.levelLB.bind('<Delete>', self.delete_competitor)
        self.sexLB.bind('<Delete>', self.delete_competitor)
        self.ageLB.bind('<Delete>', self.delete_competitor)

        self.idLB.bind('<Double-Button-1>', self.edit_competitor)
        self.fnameLB.bind('<Double-Button-1>', self.edit_competitor)
        self.lnameLB.bind('<Double-Button-1>', self.edit_competitor)
        self.levelLB.bind('<Double-Button-1>', self.edit_competitor)
        self.sexLB.bind('<Double-Button-1>', self.edit_competitor)
        self.ageLB.bind('<Double-Button-1>', self.edit_competitor)

        self.idLB.bind('<FocusOut>', lambda e: self.idLB.selection_clear(0, 'end'))  # these binds ensure that when
        self.fnameLB.bind('<FocusOut>', lambda e: self.fnameLB.selection_clear(0, 'end'))  # leaving the table there
        self.lnameLB.bind('<FocusOut>', lambda e: self.lnameLB.selection_clear(0, 'end'))  # doesn't remain a selection
        self.levelLB.bind('<FocusOut>', lambda e: self.levelLB.selection_clear(0, 'end'))  # despite not having focus
        self.sexLB.bind('<FocusOut>', lambda e: self.sexLB.selection_clear(0, 'end'))
        self.ageLB.bind('<FocusOut>', lambda e: self.ageLB.selection_clear(0, 'end'))

        scrollbar.config(command=self.set_scrollables)

        scrollbar.pack(side='right', fill='y', expand=True)
        self.idLB.pack(side='left', fill='y', expand=True)
        self.fnameLB.pack(side='left', fill='y', expand=True)
        self.lnameLB.pack(side='left', fill='y', expand=True)
        self.levelLB.pack(side='left', fill='y', expand=True)
        self.sexLB.pack(side='left', fill='y', expand=True)
        self.ageLB.pack(side='left', fill='y', expand=True)
        self.editButton.pack(side='top', fill='x')
        self.registerButton.pack(side='top', fill='x', pady=10)
        self.deleteButton.pack(side='top', fill='x')

    def register_new(self):
        CompetitorRegistrationWindow(self, self.db)

    def get_selected_competitor(self):
        if len(self.idLB.curselection()) > 0:
            row = self.idLB.curselection()
        elif len(self.fnameLB.curselection()) > 0:
            row = self.fnameLB.curselection()
        elif len(self.lnameLB.curselection()) > 0:
            row = self.lnameLB.curselection()
        elif len(self.levelLB.curselection()) > 0:
            row = self.levelLB.curselection()
        elif len(self.sexLB.curselection()) > 0:
            row = self.sexLB.curselection()
        elif len(self.ageLB.curselection()) > 0:
            row = self.ageLB.curselection()  # this block searches for any selection in all the list boxes

        return row

    def delete_competitor(self, *args):
        try:
            competitor_id = self.idLB.get(self.get_selected_competitor())
        except UnboundLocalError:  # occurs when there is no competitor selected
            print('cannot delete a competitor when there is none selected')
            return
        self.db.delete_row(competitor_id)

    def edit_competitor(self, *args):
        id = self.get_selected_competitor()

        if id:
            entrytab = self.parent.parent.parent.entryTab

            entrytab.routeAttemptsEntryFrame.reset()
            enable_frame(entrytab.competitorInfoFrame)
            enable_frame(entrytab.routeAttemptsEntryFrame)
            entrytab.competitorInfoFrame.fill_competitor(self.idLB.get(id))  # fills info to entry

    def set_scrollables(self, *args):
        self.idLB.yview(*args)
        self.fnameLB.yview(*args)
        self.lnameLB.yview(*args)
        self.levelLB.yview(*args)
        self.sexLB.yview(*args)
        self.ageLB.yview(*args)

    def update_table(self, pattern=None):
        self.clear_table()
        if pattern and not pattern == 'Search competitors...':
            rows = self.db.get_specific(pattern)
        else:
            rows = self.db.get_all()
        for i, row in enumerate(rows):
            self.idLB.insert(i, row[0])
            self.fnameLB.insert(i, row[1])
            self.lnameLB.insert(i, row[2])
            self.levelLB.insert(i, row[3])
            self.sexLB.insert(i, row[4])
            self.ageLB.insert(i, row[5])

    def clear_table(self):
        self.idLB.delete(0, 'end')
        self.fnameLB.delete(0, 'end')
        self.lnameLB.delete(0, 'end')
        self.levelLB.delete(0, 'end')
        self.sexLB.delete(0, 'end')
        self.ageLB.delete(0, 'end')


# top-level window containing the entries for registering a new competitor
# child of CompetitorTable
class CompetitorRegistrationWindow(Toplevel):
    def __init__(self, parent, db, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.parent = parent
        self.db = db
        self.title('Register new competitor...')
        self.hr1 = Frame(self, height=1, width=500, bg="gray")  # creates a gray line under the registration

        self.fnameLabel = Label(self, text='First:')
        self.lnameLabel = Label(self, text='Last:')
        self.levelLabel = Label(self, text='Level:')
        self.sexLabel = Label(self, text='Sex:')
        self.ageLabel = Label(self, text='Age:')

        self.sexValue = StringVar()
        self.sexValue.set('M')

        self.levelValues = ('Beginner', 'Intermediate', 'Advanced', 'Open')

        self.fnameEntry = EntryWithPlaceholder(self, placeholder='John', width=30)
        self.lnameEntry = EntryWithPlaceholder(self, placeholder='Doe', width=30)
        self.levelEntry = Spinbox(self, values=self.levelValues)
        self.sexEntryM = Radiobutton(self, text='M', variable=self.sexValue, value='M')
        self.sexEntryF = Radiobutton(self, text='F', variable=self.sexValue, value='F')
        self.ageEntry = Spinbox(self, from_=1, to=100, width=6)
        self.registerButton = Button(self, text='Register', command=self.register_competitor)

        self.ageEntry.delete('0', 'end')
        self.ageEntry.insert(0, 20)

        self.fnameEntry.bind('<Return>', self.register_competitor)  # these bind all the entries to <return>
        self.lnameEntry.bind('<Return>', self.register_competitor)  # meaning that hitting enter while within any of
        self.levelEntry.bind('<Return>', self.register_competitor)  # of them will submit the form to the
        self.sexEntryF.bind('<Return>', self.register_competitor)  # register_competitor function
        self.sexEntryM.bind('<Return>', self.register_competitor)
        self.ageEntry.bind('<Return>', self.register_competitor)
        self.registerButton.bind('<Return>', self.register_competitor)

        self.fnameLabel.grid(row=1, column=0)
        self.fnameEntry.grid(row=1, column=1, columnspan=4)
        self.lnameLabel.grid(row=1, column=5)
        self.lnameEntry.grid(row=1, column=6, columnspan=4)
        self.levelLabel.grid(row=2, column=0)
        self.levelEntry.grid(row=2, column=1, columnspan=2)
        self.sexLabel.grid(row=2, column=3)
        self.sexEntryM.grid(row=2, column=4)
        self.sexEntryF.grid(row=2, column=5)
        self.ageLabel.grid(row=2, column=6)
        self.ageEntry.grid(row=2, column=7)
        self.registerButton.grid(row=2, column=8)

    def register_competitor(self, *args):
        self.db.insert_row((self.fnameEntry.get(),
                            self.lnameEntry.get(),
                            self.levelEntry.get(),
                            self.sexValue.get(),
                            self.ageEntry.get(),
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.clear_registration()
        self.fnameEntry.focus_set()

    def clear_registration(self):
        self.fnameEntry.replace_placeholder()
        self.lnameEntry.replace_placeholder()
        self.levelEntry.setvar(self.levelValues[0], value='1')
        self.sexValue.set('M')
        self.ageEntry.delete(0, 'end')
        self.ageEntry.insert(0, 20)


########################################################################################################################


# entry box that allows text based commands for quick functionality
# child of Application
class QuickCommand(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.config(highlightthickness=5, highlightbackground=LLBLUE, bg=LLBLUE)

        self.commandEntryLabel = Label(self, text='Enter commands:', bg=LLBLUE)
        self.commandEntry = Entry(self)
        self.executeButton = Button(self, text='Execute', bg=LBLUE, command=lambda: self.execute(self.commandEntry.get()))
        self.helpButton = Button(self, text='Usage Help...', bg=LBLUE, command=show_usage_help)

        self.commandEntryLabel.pack(side=LEFT)
        self.commandEntry.pack(side=LEFT, expand=1, fill='x')
        self.executeButton.pack(side=LEFT, padx=5)
        self.helpButton.pack(side=LEFT)

        self.commandEntry.bind('<Return>', lambda event: self.execute(self.commandEntry.get()))

    def execute(self, command):  # decides what keyword has been used in the quickCommand line
        c = command.split(' ')
        if c[0] == 'r':
            info = c[1].split('.')
            self.r(int(info[0]), [int(info[1]), int(info[2])])

        self.commandEntry.delete(0, 'end')

    def r(self, id, route):  # handles use of the 'r' keyword at the quickCommand line
        routes = [[self.db.get_row(id)[x], self.db.get_row(id)[x + 5]] for x in range(7, 12)]  # creates a list of lists, each containing a competitors' current route numbers and attempt amounts
        for rout in routes:
            if rout[0] == route[0]: # checks if a submitted route already has an entry,
                rout[0] = 0  # and sets the old one to zero if so
        routes.append(route)  # adds the new route data to that list
        routes.sort(key=lambda x: x[0])  # sorts the 2d list by the route numbers (first item in smaller lists)
        newinfo = list(self.db.get_row(id)[1:6])  # creates a new list with current competitor info
        newinfo.append(100 * sum(x[0] for x in routes[-5:]))  # appends new score to that list
        for r in routes[-5:]:
            newinfo.append(r[0])  # appends new route nums to that list
        for r in routes[-5:]:
            newinfo.append(r[1])  # appends new route attempts to that list

        self.db.update_row(id, tuple(newinfo))  # loads new info to the database
        self.parent.update_all()  # updates displays


# add merge/new dialogue for open file dialog