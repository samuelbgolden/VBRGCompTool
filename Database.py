import sqlite3

# contains all the competitors and their informations
class LocalDatabase:
    def __init__(self):  # where columns is a dictionary; keys=col names, values=data type

        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE competitors
                     (fname text, lname text, level text, sex text, age int,
                      score int, r1 int, r2 int, r3 int, r4 int, r5 int)''')

    def insert_row(self, row):  # row should be a set of values of length 11
        self.c.execute('INSERT INTO competitors VALUES (?,?,?,?,?,?,?,?,?,?,?)', row)

    def insert_rows(self, rows):
        self.c.executemany('INSERT INTO competitors VALUES (?,?,?,?,?,?,?,?,?,?,?', rows)

    def get_all(self):
        self.c.execute('SELECT * FROM competitors')
        return self.c.fetchall()

    def get_row(self, fname, lname, age):
        values = (fname, lname, age)
        self.c.execute('''SELECT * FROM competitors WHERE
                            fname = ? AND lname = ? AND age = ?''', values)