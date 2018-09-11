import sqlite3
import pymysql
import threading
import time
from tkinter import Toplevel, Entry, Label, Button

###################################################################################################################
# getters should not go to the global db first, rather local should be interacted with as it was before implementation
# of global. this will keep fluidity of usage without constantly interacting with ghost rows. setters can attempt to
# interact with the global first because these will not affect what is scene (which is to say fluidity)
# getters: get_row, get_all, get_specific, get_specific_rows_by_score
###################################################################################################################


# database containing all the competitors and their information
# accessed by nearly every class
class LocalDatabase:
    def __init__(self, parent):
        self.parent = parent

        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE competitors
                     (id integer primary key, fname text, lname text, level text, sex text, age int,
                      score int, r1 int, r2 int, r3 int, r4 int, r5 int, a1 int, a2 int, a3 int, a4 int, a5 int)''')

    def insert_row(self, row):  # row should be a set of values of length 16
        self.c.execute('''INSERT INTO competitors (fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', row)
        self.parent.update_all()

    def insert_rows(self, rows):
        self.c.executemany('''INSERT INTO competitors (id, fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', rows)
        self.parent.update_all()

    def delete_row(self, id):
        self.c.execute('''DELETE FROM competitors WHERE id = ?''', (id,))
        self.parent.update_all()

    def delete_all(self):
        self.c.execute('DELETE FROM competitors')
        self.parent.update_all()

    def get_all(self):
        self.c.execute('SELECT * FROM competitors ORDER BY lname COLLATE NOCASE')
        return self.c.fetchall()

    def get_row(self, id):
        self.c.execute('''SELECT * FROM competitors WHERE id = ?''', (id,))
        return self.c.fetchone()

    def get_specific_rows_by_score(self, pattern=None, **kwargs):  # orders by score by default
        execstring = 'SELECT id, fname, lname, score FROM competitors'
        areattributes = False

        for i, k in enumerate(kwargs.keys()):
            if i == 0:
                execstring += ' WHERE'
                areattributes = True
            if k in ('id', 'age', 'score', 'r1', 'r2', 'r3', 'r4', 'r5', 'a1', 'a2', 'a3', 'a4', 'a5'):
                execstring += " {} = {} AND".format(k, kwargs[k])
            elif k in ('fname', 'lname', 'level', 'sex'):
                execstring += " {} = '{}' AND".format(k, kwargs[k])
        if areattributes:
            execstring = execstring[:-4]  # cuts off leading ' AND'
        if pattern:
            execstring += (" AND (fname LIKE '{}' OR lname LIKE '{}' OR level LIKE '{}' OR id LIKE '{}')".format(pattern+'%', pattern+'%', pattern+'%', pattern+'%'))
        execstring += ' ORDER BY score DESC'

        self.c.execute(execstring)
        return self.c.fetchall()

    def get_specific(self, pattern):
        self.c.execute('''SELECT * from competitors WHERE fname LIKE ? OR
                                                          lname LIKE ? OR
                                                          level LIKE ? OR
                                                          id LIKE ?''',
                       (pattern+'%', pattern+'%', pattern+'%', pattern+'%'))
        return self.c.fetchall()

    def update_row(self, id, info):
        ordered = info + (id,)
        self.c.execute('''UPDATE competitors 
                          SET fname = ?, lname = ?, level = ?, sex = ?, age = ?, 
                          score = ?, r1 = ?, r2 = ?, r3 = ?, r4 = ?, r5 = ?,
                          a1 = ?, a2 = ?, a3 = ?, a4 = ?, a5 = ?
                          WHERE id = ?''', ordered)
        self.parent.update_all()


class GlobalDatabase:
    def __init__(self, parent, user=None, password=None, address=None, database=None):
        self.parent = parent

        self.user = user
        self.password = password
        self.address = address
        self.database = database

        self.cont = True  # flag for maintaining update loop
        self.updateFlag = True
        self.delay = 3  # seconds between global database updates
        self.timer = threading.Timer(self.delay, self.update)  # creates a thread for the timer
        self.timer.start()  # starts timer in separate thread
        self.unsyncedRows = []

        self.old = []  # this will be what was in the database on the last update call.
        # on each call, I will compare the last update to this current, to determine if the application
        # needs to be updated
        self.new = []

        self.conn = None

    def update(self):
        print("~~~~~~~~~~ update func call at:", time.time(), "~~~~~~~~~~")

        if self.cont:
            self.timer = threading.Timer(self.delay, self.update)  # creates a thread for the timer
            self.timer.start()  # starts timer in separate thread
        self.updateFlag = True

    def update_main(self):
        if self.updateFlag:
            try:
                while self.unsyncedRows:
                    print('tending to unsynced rows:', self.unsyncedRows)
                    if self.unsyncedRows[0][0] == 'INSERT':     # the redundancy in these if blocks
                        item = self.unsyncedRows[0]             # is necessary, because we want to keep
                        self.insert_row(item[1])       # the unsynced row in the list if the action
                        self.unsyncedRows.pop(0)                # returns an error
                    elif self.unsyncedRows[0][0] == 'DELETE':
                        item = self.unsyncedRows[0]
                        self.delete_row(item[1])
                        self.unsyncedRows.pop(0)
                    elif self.unsyncedRows[0][0] == 'DELETE ALL':
                        self.delete_all()
                        self.unsyncedRows.pop(0)
                    elif self.unsyncedRows[0][0] == 'UPDATE':
                        item = self.unsyncedRows[0]
                        self.update_row(item[1], item[2])
                        self.unsyncedRows.pop(0)
            except pymysql.Error:
                pass
            self.new = self.get_all()
            if not self.old == self.new:
                self.parent.update_all()
                self.old = self.new
            self.updateFlag = False
        self.parent.parent.after(10, self.update_main)

    def connect(self):
        self.conn = pymysql.connect(self.address, self.user, self.password, self.database)

    def prompt(self):
        NetworkConfigurationWindow(self)

    def is_connected(self):
        try:
            self.connect()
            c = self.conn.cursor()
            c.execute('SELECT VERSION()')
            result = c.fetchone()
            if result:
                return True
            else:
                return False
        except pymysql.Error:
            pass
        return False

    def is_configured(self):
        return self.user and self.password and self.address and self.database

    def end(self):
        self.conn.commit()
        self.parent.update_all()

    def insert_row(self, row):
        try:
            self.connect()
            with self.conn.cursor() as c:
                c.execute('''INSERT INTO `competitors` (`fname`, `lname`, `level`, `sex`, `age`, `score`, `r1`, `r2`, `r3`, `r4`, `r5`, `a1`, `a2`, `a3`, `a4`, `a5`)
                                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', row)
            self.end()
        except pymysql.Error:
            self.unsyncedRows.append(('INSERT', row))

    def insert_rows(self, rows):
        print(rows)
        try:
            self.connect()
            with self.conn.cursor() as c:
                for row in rows:
                    c.execute('''INSERT INTO `competitors` (`fname`, `lname`, `level`, `sex`, `age`, `score`, `r1`, `r2`, `r3`, `r4`, `r5`, `a1`, `a2`, `a3`, `a4`, `a5`)
                                                  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', row)
            self.end()
        except pymysql.Error:
            for row in rows:
                self.unsyncedRows.append(('INSERT', row))

    def delete_row(self, id):
        try:
            self.connect()
            with self.conn.cursor() as c:
                c.execute('''DELETE FROM `competitors` WHERE `id` = %s''', (id,))
            self.end()
        except pymysql.Error:
            self.unsyncedRows.append(('DELETE', id))

    def delete_all(self):
        try:
            self.connect()
            with self.conn.cursor() as c:
                c.execute('''DELETE FROM `competitors` WHERE `id` > 0''')
            self.end()
        except pymysql.Error:
            self.unsyncedRows.append(('DELETE ALL',))

    def get_all(self):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('SELECT * FROM `competitors` ORDER BY `lname`')
            records = c.fetchall()
        return records

    def get_row(self, id):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('''SELECT * FROM `competitors` WHERE `id` = %s''', (id,))
            record = c.fetchone()
        return record

    def get_specific_rows_by_score(self, pattern=None, **kwargs):  # orders by score by default
        self.connect()

        execstring = 'SELECT `id`, `fname`, `lname`, `score` FROM `competitors`'
        areattributes = False

        for i, k in enumerate(kwargs.keys()):
            if i == 0:
                execstring += ' WHERE'
                areattributes = True
            if k in ('id', 'age', 'score', 'r1', 'r2', 'r3', 'r4', 'r5', 'a1', 'a2', 'a3', 'a4', 'a5'):
                execstring += ' {} = {} AND'.format(k, kwargs[k])
            elif k in ('fname', 'lname', 'level', 'sex'):
                execstring += ' {} = \'{}\' AND'.format(k, kwargs[k])
        if areattributes:
            execstring = execstring[:-4]  # cuts off leading ' AND'
        if pattern:
            execstring += (" AND (fname LIKE '{}' OR lname LIKE '{}' OR level LIKE '{}' OR id LIKE '{}')".format(pattern+'%', pattern+'%', pattern+'%', pattern+'%'))
        execstring += ' ORDER BY score DESC'

        with self.conn.cursor() as c:
            c.execute(execstring)
            records = c.fetchall()
        return records

    def get_specific(self, pattern):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('''SELECT * from `competitors` WHERE `fname` LIKE %s OR
                                                          `lname` LIKE %s OR
                                                          `level` LIKE %s OR
                                                          `id` LIKE %s''',
                       (pattern+'%', pattern+'%', pattern+'%', pattern+'%'))
            records = c.fetchall()
        return records

    def update_row(self, id, info):
        try:
            self.connect()
            ordered = info + (id,)
            with self.conn.cursor() as c:
                c.execute('''UPDATE `competitors` 
                                            SET `fname` = %s, `lname` = %s, `level` = %s, `sex` = %s, `age` = %s, 
                                            `score` = %s, `r1` = %s, `r2` = %s, `r3` = %s, `r4` = %s, `r5` = %s,
                                            `a1` = %s, `a2` = %s, `a3` = %s, `a4` = %s, `a5` = %s
                                            WHERE `id` = %s''', ordered)
            self.end()
        except pymysql.Error:
            self.unsyncedRows.append(('UPDATE', id, info))


class NetworkConfigurationWindow(Toplevel):
    def __init__(self, parent, *args, **kwargs):
        Toplevel.__init__(self, *args, **kwargs)
        self.parent = parent

        self.title('Database Connection Info')
        self.userLabel = Label(self, text='Database user:')
        self.passwordLabel = Label(self, text='Database user password:')
        self.addressLabel = Label(self, text='Host machine address:')
        self.databaseLabel = Label(self, text='Database name:')
        self.userEntry = Entry(self)
        self.passwordEntry = Entry(self)
        self.addressEntry = Entry(self)
        self.databaseEntry = Entry(self)
        self.saveButton = Button(self, text='Save', command=self.save)
        self.connectButton = Button(self, text='Connect', command=self.parent.connect)

        self.userLabel.grid(row=0, column=0)
        self.userEntry.grid(row=0, column=1)
        self.passwordLabel.grid(row=1, column=0)
        self.passwordEntry.grid(row=1, column=1)
        self.addressLabel.grid(row=2, column=0)
        self.addressEntry.grid(row=2, column=1)
        self.databaseLabel.grid(row=3, column=0)
        self.databaseEntry.grid(row=3, column=1)
        self.saveButton.grid(row=4, column=0, pady=5)
        self.connectButton.grid(row=4, column=1, pady=5)

    def save(self):
        self.parent.user = self.userEntry.get()
        self.parent.password = self.passwordEntry.get()
        self.parent.address = self.addressEntry.get()
        self.parent.database = self.databaseEntry.get()
