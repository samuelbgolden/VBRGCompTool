from tkinter.filedialog import *
from tkinter.messagebox import askyesnocancel
import csv
import os


class IOHandler:
    def __init__(self, parent, db):
        self.filename = ''
        self.db = db
        self.parent = parent

    def new(self):
        if self.filename == '' and len(self.db.get_all()) == 0:
            return
        else:
            a = askyesnocancel("Before you open...", "Would you like to save the current competition?")
            if a:
                self.save()
            elif a is None:
                return
        self.db.delete_all()
        self.filename = ''
        self.parent.parent.title('New Competition')
        self.parent.competitionTab.competitionFrame.competitorTable.update_table()

    def save(self):
        if self.filename == '':
            self.save_as()
        else:
            self.write_all()

    def save_as(self):
        self.filename = asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("CSV File", "*.csv"), ("all files", "*.*")))
        self.write_all()

    def open(self):
        if not(len(self.db.get_all()) == 0):
            a = askyesnocancel("Before you open...", "Would you like to save the current competition?")
            if a:
                self.save()
            elif a is None:
                return
        self.filename = askopenfilename(initialdir="C:/", title="Open file",
                                        filetypes=(("CSV File", "*.csv"), ("all files", "*.*")))
        self.db.delete_all()
        with open(self.filename, 'r', newline='') as file:
            reader = csv.reader(file)
            self.db.delete_all()
            self.parent.competitionTab.competitionFrame.competitorTable.update_table()
            self.db.insert_rows(reader)
        self.parent.competitionTab.competitionFrame.competitorTable.update_table()
        self.parent.parent.title('Working in competition at ' + os.path.splitext(self.filename)[0])

    def write_all(self):
        if '.csv' not in self.filename:
            self.filename = self.filename + '.csv'
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for line in self.db.get_all():
                writer.writerow(line)

    def close(self):
        if not(self.filename == '' and len(self.db.get_all()) == 0):
            self.save()
        self.parent.parent.destroy()
