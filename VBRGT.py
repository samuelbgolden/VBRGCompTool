import tkinter as tk
from tkinter.ttk import PanedWindow
from Positionals import *
from Database import LocalDatabase
from IOHandler import IOHandler


# its everything
class Application(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('New Competition')

        self.config(bg=LBLUE)

        self.localDatabase = LocalDatabase()
        self.ioHandler = IOHandler(self, self.localDatabase)

        self.menubar = MenuBar(self, self.localDatabase, self.ioHandler)
        self.standingsTab = StandingsTab(self, self.localDatabase)
        self.entryTab = EntryTab(self, self.localDatabase)
        self.competitorTab = CompetitorTab(self, self.localDatabase)
        self.parent.configure(menu=self.menubar)

        self.competitorTab.pack(side='left', anchor='nw', fill='y', expand=1)
        self.entryTab.pack(side='left', anchor='nw', fill='y', expand=1)
        self.standingsTab.pack(side='left', anchor='nw', fill='y', expand=1)

        self.parent.protocol('WM_DELETE_WINDOW', self.ioHandler.close)


# even more everything
if __name__ == '__main__':
    root = tk.Tk()
    Application(root).pack(expand=1, fill='both')
    root.mainloop()
