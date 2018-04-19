from tkinter import Menu, Frame, Button, Radiobutton, LabelFrame, Label, Spinbox, W, E, S, N
from Interactives import *


# the white bar that contains 'File' and the associated commands
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
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent

        self.competitorSelectionFrame = LabelFrame(self, text='Competitors')
        self.filteredNameFrame = LabelFrame(self, text='Competitors')
        self.routesFrame = LabelFrame(self, text='Routes')

        self.competitorSelectionFrame.grid(row=0, column=0)
        self.filteredNameFrame.grid(row=0, column=0)
        self.routesFrame.grid(row=1, column=0)

        self.filteredNameFrame.grid_remove()


# a full tab of the notebook, containing standings and competitor list
# child of application, 'added' to notebook
class CompetitionTab(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.standingsFrame = LabelFrame(self, text='Standings', width=100)
        self.competitorsFrame = CompetitionFrame(self, db)

        self.standingsFrame.pack(side='left', fill='y')
        self.competitorsFrame.pack(side='right', fill='y')


# frame containing the registration and table of competitors
# child of CompetitionTab
class CompetitionFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db
        self.hr1 = Frame(self, height=1, width=500, bg="gray")

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

        self.registrationLabel.grid(row=0, column=0, columnspan=10, sticky=W)
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

        self.hr1.grid(row=3, column = 0, columnspan=10)

        self.competitorTableFrame = CompetitorTable(self)

        self.competitorTableFrame.grid(row=4, column=0, columnspan=10, sticky=W)

    def register_competitor(self):
        self.db.insert_row((self.fnameEntry.get(),
                            self.lnameEntry.get(),
                            self.levelEntry.get(),
                            self.sexValue.get(),
                            self.ageEntry.get(),
                            0, 0, 0, 0, 0, 0))
        self.clear_registration()
        print(self.db.get_all())

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
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.columnHeads = ('FIRST', 'LAST', 'LEVEL', 'SEX', 'AGE', 'SCORE', 'ROUTES')
        self.fnameLabel = Label(self, text='FIRST')
        self.fnameLabel.grid(row=0, column=0, columnspan=2, sticky=W)
        self.lnameLabel = Label(self, text='LAST').grid(row=0, column=2, columnspan=2, sticky=W)
        self.levelLabel = Label(self, text='LEVEL').grid(row=0, column=4, sticky=W)
        self.sexLabel = Label(self, text='SEX').grid(row=0, column=5, sticky=W)
        self.ageLabel = Label(self, text='AGE').grid(row=0, column=6, sticky=W)
        self.scoreLabel = Label(self, text='SCORE').grid(row=0, column=7, sticky=W)
        self.scoreLabel = Label(self, text='ROUTES').grid(row=0, column=8, columnspan=2, sticky=W)