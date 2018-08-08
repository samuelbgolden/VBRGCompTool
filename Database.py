import sqlite3
import pymysql
import threading
import time
from tkinter import Toplevel, Entry, Label, Button


# because the global database will not always be accessible, but the interaction with the data
# should remain fluid and uninterrupted, this handler will dynamically switch between the local
# and global databases depending on whether or not the global database is currently accessible
class DatabaseHandler:
    def __init__(self, parent):
        self.parent = parent

        self.cont = True  # flag for maintaining update loop
        self.updateFlag = False
        self.delay = 5  # seconds between global database updates
        self.timer = threading.Timer(self.delay, self.update)  # creates a thread for the timer
        self.timer.start()  # starts timer in separate thread

        self.localdb = LocalDatabase(self)
        self.globaldb = GlobalDatabase(self)

        self.unsyncedRows = []

    def update(self):
        print("update func call at:", time.time())

        if self.cont:
            self.timer = threading.Timer(self.delay, self.update)  # creates a thread for the timer
            self.timer.start()  # starts timer in separate thread
        self.updateFlag = True

    def update_main(self):
        if self.updateFlag:
            try:
                while self.unsyncedRows:
                    print('unsyncedRows:', self.unsyncedRows)
                    if self.unsyncedRows[0][0] == 'INSERT':
                        item = self.unsyncedRows.pop(0)
                        self.globaldb.insert_row(item[1])
                    elif self.unsyncedRows[0][0] == 'DELETE':
                        item = self.unsyncedRows.pop(0)
                        self.globaldb.delete_row(item[1])
                    elif self.unsyncedRows[0][0] == 'DELETE ALL':
                        self.unsyncedRows.pop(0)
                        self.globaldb.delete_all()
                    elif self.unsyncedRows[0][0] == 'UPDATE':
                        item = self.unsyncedRows.pop(0)
                        self.globaldb.update_row(item[1], item[2])
                print('out of while loop')
                globalrows = self.globaldb.get_all()
                print('global rows gotten')
                self.localdb.delete_all()
                print('local rows deleted')
                self.localdb.insert_rows(globalrows)
                print('new local rows inserted')
            except pymysql.Error:
                print('connection error')
            print('-----------------------------------------------')
            self.updateFlag = False
        self.parent.parent.after(1000, self.update_main)

    def insert_row(self, row):
        self.localdb.insert_row(row)
        try:
            self.globaldb.insert_row(row)
        except pymysql.Error:
            self.unsyncedRows.append(('INSERT', row))

    def insert_rows(self, rows):
        self.localdb.insert_rows(rows)
        try:
            self.globaldb.insert_rows(rows)
        except pymysql.Error:
            for row in rows:
                self.unsyncedRows.append(('INSERT', row))

    def delete_row(self, id):
        self.localdb.delete_row(id)
        try:
            self.globaldb.delete_row(id)
        except pymysql.Error:
            self.unsyncedRows.append(('DELETE', id))

    def delete_all(self):
        self.localdb.delete_all()
        try:
            self.globaldb.delete_all()
        except pymysql.Error:
            self.unsyncedRows.append(('DELETE ALL',))

    def get_all(self):
        try:
            rows = self.globaldb.get_all()
        except pymysql.Error:
            rows = self.localdb.get_all()
        return rows

    def get_row(self, id):
        try:
            row = self.globaldb.get_row(id)
        except pymysql.Error:
            row = self.localdb.get_row(id)
        return row

    def get_specific_rows_by_score(self, **kwargs):
        try:
            rows = self.globaldb.get_specific_rows_by_score(**kwargs)
        except pymysql.Error:
            rows = self.localdb.get_specific_rows_by_score(**kwargs)
        return rows

    def get_specific(self, pattern):
        try:
            rows = self.globaldb.get_specific(pattern)
        except pymysql.Error:
            rows = self.localdb.get_specific(pattern)
        return rows

    def update_row(self, id, info):
        self.localdb.update_row(id, info)
        try:
            self.globaldb.update_row(id, info)
        except pymysql.Error:
            self.unsyncedRows.append(('UPDATE', id, info))


# database containing all the competitors and their information
# accessed by nearly every class
class LocalDatabase:
    def __init__(self, parent):
        self.parent = parent

        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE competitors
                     (id integer, fname text, lname text, level text, sex text, age int,
                      score int, r1 int, r2 int, r3 int, r4 int, r5 int, a1 int, a2 int, a3 int, a4 int, a5 int)''')

    def insert_row(self, row):  # row should be a set of values of length 16
        self.c.execute('''INSERT INTO competitors (fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', row)
        self.parent.parent.update_all()

    def insert_rows(self, rows):
        self.c.executemany('''INSERT INTO competitors (id, fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', rows)
        self.parent.parent.update_all()

    def delete_row(self, id):
        self.c.execute('''DELETE FROM competitors WHERE id = ?''', (id,))
        self.parent.parent.update_all()

    def delete_all(self):
        self.c.execute('DELETE FROM competitors')
        self.parent.parent.update_all()

    def get_all(self):
        self.c.execute('SELECT * FROM competitors ORDER BY lname COLLATE NOCASE')
        return self.c.fetchall()

    def get_row(self, id):
        self.c.execute('''SELECT * FROM competitors WHERE id = ?''', (id,))
        return self.c.fetchone()

    def get_specific_rows_by_score(self, **kwargs):  # orders by score by default
        execstring = 'SELECT id, fname, lname, score FROM competitors'
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
            execstring = execstring[:-4] + ' ORDER BY score DESC'

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
        self.conn = None

    def connect(self):
        self.conn = pymysql.connect(self.address, self.user, self.password, self.database)

    def prompt(self):
        NetworkConfigurationWindow(self)

    def is_connected(self):
        try:
            self.conn = pymysql.connect(self.address, self.user, self.password, self.database)
            c = self.conn.cursor()
            c.execute('SELECT VERSION()')
            result = c.fetchone()
            if result:
                return True
            else:
                return False
        except pymysql.Error:
            print('ERROR IN CONNECTION')
        return False

    def is_configured(self):
        return self.user and self.password and self.address and self.database

    def end(self):
        self.conn.commit()
        self.parent.parent.update_all()
        self.conn.close()

    def insert_row(self, row):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('''INSERT INTO `competitors` (`fname`, `lname`, `level`, `sex`, `age`, `score`, `r1`, `r2`, `r3`, `r4`, `r5`, `a1`, `a2`, `a3`, `a4`, `a5`)
                                  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', row)
        self.end()

    def insert_rows(self, rows):
        self.connect()
        with self.conn.cursor() as c:
            for row in rows:
                c.execute('''INSERT INTO `competitors` (`fname`, `lname`, `level`, `sex`, `age`, `score`, `r1`, `r2`, `r3`, `r4`, `r5`, `a1`, `a2`, `a3`, `a4`, `a5`)
                                  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', row)
        self.end()

    def delete_row(self, id):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('''DELETE FROM `competitors` WHERE `id` = %s''', (id,))
        self.end()

    def delete_all(self):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('''DELETE FROM `competitors` WHERE `id` > 0''')
        self.delete_all()

    def get_all(self):
        self.connect()
        print('connected')
        with self.conn.cursor() as c:
            print('in with loop')
            c.execute('SELECT * FROM `competitors` ORDER BY `lname`')
            print('executed')
            records = c.fetchall()
            print('records gotten')
        print('out of with')
        self.conn.close()
        print('conn closed')
        return records

    def get_row(self, id):
        self.connect()
        with self.conn.cursor() as c:
            c.execute('''SELECT * FROM `competitors` WHERE `id` = %s''', (id,))
            record = c.fetchone()
        self.end()
        return record

    def get_specific_rows_by_score(self, **kwargs):  # orders by score by default
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
            execstring = execstring[:-4] + ' ORDER BY `score` DESC'

        with self.conn.cursor() as c:
            c.execute(execstring)
            records = c.fetchall()
        self.end()
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
        self.end()
        return records

    def update_row(self, id, info):
        self.connect()

        ordered = info + (id,)
        with self.conn.cursor() as c:
            c.execute('''UPDATE `competitors` 
                            SET `fname` = %s, `lname` = %s, `level` = %s, `sex` = %s, `age` = %s, 
                            `score` = %s, `r1` = %s, `r2` = %s, `r3` = %s, `r4` = %s, `r5` = %s,
                            `a1` = %s, `a2` = %s, `a3` = %s, `a4` = %s, `a5` = %s
                            WHERE `id` = %s''', ordered)
        self.end()


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
