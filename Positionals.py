from tkinter import Menu, Radiobutton, LabelFrame, Spinbox, W, E, S, N, Scrollbar, LEFT, Grid, TOP
from Interactives import *


# the gray bar that contains 'File' and the associated commands
# child of application
class MenuBar(Menu):
    def __init__(self, parent, *args, **kwargs):
        Menu.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label="New Competition")
        self.filemenu.add_command(label="Save")
        self.filemenu.add_command(label="Save as...")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Open")
        self.filemenu.add_command(label="Export")
        self.filemenu.add_command(label="Print")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close")

        self.add_cascade(label="File", menu=self.filemenu)


# a full tab frame in the notebook, containing name buttons and routes
# child of Application, 'added' to notebook
class EntryTab(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.competitorInfoFrame = CompetitorInfoFrame(self, self.db)
        self.routeAttemptsEntryFrame = RouteAttemptsEntryFrame(self, self.db)

        self.routeAttemptsEntryFrame.pack(side=LEFT, fill='y', anchor=N+W, padx=20)
        self.competitorInfoFrame.pack(side=TOP, anchor=N+W)


class RouteAttemptsEntryFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.routes = [RouteAttemptsEntry(self, x) for x in range(1, 51)]

        for i, route in enumerate(self.routes):
            if i < 25:
                route.grid(row=i % 25, column=0)
            else:
                route.grid(row=i % 25, column=2)
        Frame(self, width=2, bg='dark gray').grid(row=0, rowspan=25, column=1, stick='nsew', padx=10)

    def get_selected_routes(self):
        selected = []
        for route in self.routes:
            if route.numLabel.cget('bg') == 'green':
                selected.append(route)
        return selected

    def reset(self):
        for route in self.routes:
            route.reset()

    def notFiveRoutesSelected(self):
        count = 0
        for route in self.routes:
            if route.numLabel.cget('bg') == 'green':  # checks if route is selected
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

        self.sexValue = StringVar()
        self.idValue = IntVar()
        self.levelValues = ('Beginner', 'Intermediate', 'Advanced', 'Open')
        self.routeValues = [StringVar()]

        self.routeListingFrame = Frame(self)

        self.idValueLabel = Label(self, textvariable=self.idValue)
        self.idLabel = Label(self, text='ID: ')
        self.frameTitleLabel = Label(self, text="COMPETITOR INFO")
        self.fnameLabel = Label(self, text='FIRST:')
        self.lnameLabel = Label(self, text='LAST:')
        self.levelLabel = Label(self, text='LEVEL:')
        self.sexLabel = Label(self, text='SEX:')
        self.ageLabel = Label(self, text='AGE:')
        self.routesLabel = Label(self.routeListingFrame, text='ROUTES:')
        self.attemptsLabel = Label(self.routeListingFrame, text='ATTEMPTS:')

        self.fnameEntry = Entry(self, width=30)
        self.lnameEntry = Entry(self, width=30)
        self.levelEntry = Spinbox(self, values=self.levelValues, width=28)
        self.sexEntryM = Radiobutton(self, text='M', variable=self.sexValue, value='M')
        self.sexEntryF = Radiobutton(self, text='F', variable=self.sexValue, value='F')
        self.ageEntry = Spinbox(self, from_=1, to=100, width=10)
        self.routeEntries = [Entry(self.routeListingFrame, width=3) for _ in range(5)]
        self.attemptEntries = [Entry(self.routeListingFrame, width=3) for _ in range(5)]

        self.updateButton = Button(self, text='Update Competitor', command=self.update_competitor)

        self.frameTitleLabel.grid(stick='nw', row=0, column=0, columnspan=6)
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
        self.routesLabel.grid(stick='nse', row=0, column=0)
        for i, entry in enumerate(self.routeEntries):
            Label(self.routeListingFrame, text=i+1, fg='white', bg='dark gray')\
                .grid(column=2*i+1, row=0, rowspan=2, stick='ns')
            entry.grid(stick='nw', row=0, column=2*i+2)
        self.attemptsLabel.grid(stick='nse', row=1, column=0)
        for i, entry in enumerate(self.attemptEntries):
            entry.grid(stick='nw', row=1, column=2*i+2)
        self.updateButton.grid(row=8, column=0, columnspan=6)

        for i in range(0, Grid.grid_size(self)[0]):
            Grid.grid_rowconfigure(self, i, weight=1)
        for i in (0, Grid.grid_size(self)[0]):
            Grid.grid_columnconfigure(self, i, weight=1)
        for i in (0, Grid.grid_size(self.routeListingFrame)[0]):
            Grid.grid_rowconfigure(self.routeListingFrame, i, weight=1)
        for i in (0, Grid.grid_size(self.routeListingFrame)[0]):
            Grid.grid_columnconfigure(self.routeListingFrame, i, weight=1)

    def fill_competitor(self, id):
        row = self.db.get_row(id)
        self.clear_competitor()
        self.idValue.set(id)
        self.fnameEntry.insert(0, row[1])
        self.lnameEntry.insert(0, row[2])
        self.levelEntry.insert(0, row[3])
        self.sexValue.set(row[4])
        self.ageEntry.insert(0, row[5])
        #need score thing here for row[6]
        for i in range(0, 5):
            self.routeEntries[i].insert(0, row[i+7])
            self.attemptEntries[i].insert(0, row[i+12])
            self.parent.routeAttemptsEntryFrame.routes[row[i+7]].attemptsAmt.set(row[i+12])
            self.parent.routeAttemptsEntryFrame.routes[row[i+7]].numLabel.configure(bg='green', fg='white')

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

    def update_from_route_buttons(self):
        selected = self.parent.routeAttemptsEntryFrame.get_selected_routes()
        for i in range(0, 5):
            self.routeEntries[i].delete(0, 'end')
            self.attemptEntries[i].delete(0, 'end')
            try:
                self.routeEntries[i].insert(0, selected[i].num)
                self.attemptEntries[i].insert(0, selected[i].attemptsAmt.get())
            except IndexError:
                break

    def update_competitor(self):
        self.db.update_row(self.idValue.get(),
                           (self.fnameEntry.get(),
                            self.lnameEntry.get(),
                            self.levelEntry.get(),
                            self.sexValue.get(),
                            self.ageEntry.get(),
                            self.calc_score(),
                            self.routeEntries[0].get(),
                            self.routeEntries[1].get(),
                            self.routeEntries[2].get(),
                            self.routeEntries[3].get(),
                            self.routeEntries[4].get(),
                            self.attemptEntries[0].get(),
                            self.attemptEntries[1].get(),
                            self.attemptEntries[2].get(),
                            self.attemptEntries[3].get(),
                            self.attemptEntries[4].get()))
        self.parent.parent.competitionTab.competitionFrame.competitorTable.update_table()

    def calc_score(self):
        score = 0
        for entry in self.routeEntries:
            score += int(entry.get()) * 100  # currently throws ValueError on an empty entry box
        return score                         # a series of try statements would probably be best here


# a full tab of the notebook, containing standings and competitor list
# child of application, 'added' to notebook
class CompetitionTab(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.standingsFrame = LabelFrame(self, text='Standings', width=100)
        self.competitionFrame = CompetitionFrame(self, db)

        self.competitionFrame.pack(side='right', fill='y', expand=1, anchor=E)
        self.standingsFrame.pack(side='left', fill='both', expand=4)


# frame containing the registration and table of competitors
# child of CompetitionTab
class CompetitionFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db
        self.hr1 = Frame(self, height=1, width=500, bg="gray")  # creates a gray line under the registration

        self.registrationLabel = Label(self, text='Register a new competitor...', fg='gray')
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
        self.sexEntryF.bind('<Return>', self.register_competitor)   # register_competitor function
        self.sexEntryM.bind('<Return>', self.register_competitor)
        self.ageEntry.bind('<Return>', self.register_competitor)
        self.registerButton.bind('<Return>', self.register_competitor)

        self.registrationLabel.grid(row=0, column=0, columnspan=10)
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

        # END REGISTRATION SECTION #################

        self.hr1.grid(stick='nsew', row=3, column=0, columnspan=10)

        self.competitorTable = CompetitorTable(self, self.db)

        self.competitorTable.grid(row=4, column=0, columnspan=10, sticky=W+S+N, rowspan=10)
        Grid.grid_rowconfigure(self, 4, weight=1)

    def register_competitor(self, *args):
        self.db.insert_row((self.fnameEntry.get(),
                            self.lnameEntry.get(),
                            self.levelEntry.get(),
                            self.sexValue.get(),
                            self.ageEntry.get(),
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.clear_registration()
        self.competitorTable.update_table()
        self.fnameEntry.focus_set()

    def clear_registration(self):
        self.fnameEntry.replace_placeholder()
        self.lnameEntry.replace_placeholder()
        self.levelEntry.setvar(self.levelValues[0], value='1')
        self.sexValue.set('M')
        self.ageEntry.delete(0, 'end')
        self.ageEntry.insert(0, 20)


# frame that holds all the records of the competitors
# child of CompetitionFrame
class CompetitorTable(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        scrollbar = Scrollbar(self)
        self.idLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=3)
        self.fnameLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=25)
        self.lnameLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=25)
        self.levelLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=12)
        self.sexLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=2)
        self.ageLB = Listbox(self, yscrollcommand=scrollbar.set, borderwidth=0, width=3)
        self.deleteButton = Button(self, bg='red', fg='white', text="DELETE\nSELECTED",
                                   borderwidth=1, command=self.delete_competitor)
        self.editButton = Button(self, bg='dark green', fg='white', text="EDIT\nSELECTED",
                                 borderwidth=1, command=self.edit_competitor)
        self.idLB.bind('<Delete>', self.delete_competitor)
        self.fnameLB.bind('<Delete>', self.delete_competitor)
        self.lnameLB.bind('<Delete>', self.delete_competitor)
        self.levelLB.bind('<Delete>', self.delete_competitor)
        self.sexLB.bind('<Delete>', self.delete_competitor)
        self.ageLB.bind('<Delete>', self.delete_competitor)

        scrollbar.config(command=self.set_scrollables)

        scrollbar.pack(side='right', fill='y', expand=True)
        self.idLB.pack(side='left', fill='y', expand=True)
        self.fnameLB.pack(side='left', fill='y', expand=True)
        self.lnameLB.pack(side='left', fill='y', expand=True)
        self.levelLB.pack(side='left', fill='y', expand=True)
        self.sexLB.pack(side='left', fill='y', expand=True)
        self.ageLB.pack(side='left', fill='y', expand=True)
        self.editButton.pack(side='top')
        self.deleteButton.pack(side='bottom')

    def get_selected_competitor(self):
        row = 0
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
        self.db.delete_row(self.idLB.get(self.get_selected_competitor()))
        self.update_table()

    def edit_competitor(self, *args):
        id = self.get_selected_competitor()
        self.parent.parent.parent.notebook.select(1)  # moves to entry tab in notebook
        self.parent.parent.parent.entryTab.routeAttemptsEntryFrame.reset()
        self.parent.parent.parent.entryTab.competitorInfoFrame.fill_competitor(self.idLB.get(id))  # fills info to entry

    def set_scrollables(self, *args):
        self.idLB.yview(*args)
        self.fnameLB.yview(*args)
        self.lnameLB.yview(*args)
        self.levelLB.yview(*args)
        self.sexLB.yview(*args)
        self.ageLB.yview(*args)

    def update_table(self):
        self.clear_table()
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