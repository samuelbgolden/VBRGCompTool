import tkinter as tk
from tkinter.ttk import Notebook
from Positionals import *
from Database import LocalDatabase


class Application(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.localDatabase = LocalDatabase()

        self.menubar = MenuBar(self)
        self.notebook = Notebook(self)
        self.entryTab = EntryTab(self)
        self.competitionTab = CompetitionTab(self, self.localDatabase)

        self.parent.configure(menu=self.menubar)
        self.entryTab.pack(fill='both', expand=1)
        self.competitionTab.pack(fill='both', expand=1)
        self.notebook.add(self.competitionTab, text='Competition')
        self.notebook.add(self.entryTab, text='Score Entry')
        self.notebook.pack(fill="both")


if __name__ == '__main__':
    root = tk.Tk()
    Application(root).pack()
    root.mainloop()