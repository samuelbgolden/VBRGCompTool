from tkinter.filedialog import *
from tkinter.messagebox import askyesnocancel
import csv
import os


# handles all the stuff in the 'File' menu at the top left; i.e. saving, closing, opening, exporting files
# most frequently accessed by the MenuBar class
class IOHandler:
    def __init__(self, parent, db):
        self.filename = ''
        self.db = db
        self.parent = parent

    def new(self):
        if self.is_saved():
            return
        else:
            a = prompt_save()
            if a:
                self.save()
            elif a is None:
                return
        self.db.delete_all()
        self.filename = ''
        self.parent.parent.title('New Competition')

    def save(self):
        if self.filename == '':
            self.save_as()
        else:
            self.write_all()

    def save_as(self):
        self.filename = asksaveasfilename(initialdir="C:/", title="Save as...", filetypes=(("CSV File", "*.csv"), ("all files", "*.*")))
        self.write_all()

    def open(self):
        if not self.is_saved():
            a = prompt_save()
            if a:
                self.save()
            elif a is None:
                return
        self.filename = askopenfilename(initialdir="C:/", title="Open file",
                                        filetypes=(("CSV File", "*.csv"), ("all files", "*.*")))
        with open(self.filename, 'r', newline='') as file:
            reader = csv.reader(file)
            self.db.localdb.delete_all()
            self.db.insert_rows(reader)
        self.parent.parent.title('Working in competition at ' + os.path.splitext(self.filename)[0])

    def write_all(self):
        if '.csv' not in self.filename:
            self.filename = self.filename + '.csv'
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for line in self.db.get_all():
                writer.writerow(line)

    def is_saved(self):
        csvstuff = self.read_all_from_csv()
        dbstuff = self.db.get_all()
        if len(csvstuff) != len(dbstuff):
            return False
        for i, lst in enumerate(csvstuff):
            for j, item in enumerate(lst):
                if '{}'.format(item) != '{}'.format(dbstuff[i][j]):
                    return False
        return True

    def read_all_from_csv(self):
        try:
            with open(self.filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                return [row for row in reader]
        except FileNotFoundError:
            return []

    def close(self):
        if not self.is_saved():
            a = prompt_save()
            if a:
                self.save()
            elif a is None:
                return
        self.parent.databaseHandler.cont = False
        self.parent.parent.destroy()


def prompt_save():
    return askyesnocancel("Save", "Do you want to save the current competition?")