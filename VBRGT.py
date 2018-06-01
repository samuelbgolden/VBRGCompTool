import tkinter as tk
from tkinter.ttk import Notebook
from Positionals import *
from Database import LocalDatabase
from IOHandler import IOHandler


# its everything
class Application(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('New Competition')

        self.localDatabase = LocalDatabase()
        self.ioHandler = IOHandler(self, self.localDatabase)

        self.menubar = MenuBar(self, self.localDatabase, self.ioHandler)
        self.notebook = Notebook(self)
        self.entryTab = EntryTab(self, self.localDatabase)
        self.competitionTab = CompetitionTab(self, self.localDatabase)
        self.parent.configure(menu=self.menubar)

        self.entryTab.pack(fill='both', expand=1)
        self.competitionTab.pack(fill='both', expand=1)

        self.notebook.add(self.competitionTab, text='Competition')
        self.notebook.add(self.entryTab, text='Score Entry')
        self.notebook.pack(fill='both', expand=1)

        self.parent.protocol('WM_DELETE_WINDOW', self.ioHandler.close)


# even more everything
if __name__ == '__main__':
    root = tk.Tk()
    Application(root).pack(expand=1, fill='both')
    root.mainloop()
