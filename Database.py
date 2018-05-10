import sqlite3


# contains all the competitors and their information
class LocalDatabase:
    def __init__(self):  # where columns is a dictionary; keys=col names, values=data type

        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE competitors
                     (id integer PRIMARY KEY AUTOINCREMENT, fname text, lname text, level text, sex text, age int,
                      score int, r1 int, r2 int, r3 int, r4 int, r5 int, a1 int, a2 int, a3 int, a4 int, a5 int)''')

    def insert_row(self, row):  # row should be a set of values of length 16
        self.c.execute('''INSERT INTO competitors (fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', row)

    def insert_rows(self, rows):
        self.c.executemany('''INSERT INTO competitors (fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', rows)

    def delete_row(self, id):
        self.c.execute('''DELETE FROM competitors WHERE id = ?''', (id,))

    def get_all(self):
        self.c.execute('SELECT * FROM competitors ORDER BY lname COLLATE NOCASE')
        return self.c.fetchall()

    def get_row(self, id):
        self.c.execute('''SELECT * FROM competitors WHERE id = ?''', (id,))
        return self.c.fetchone()

    def update_row(self, id, info):
        ordered = info + (id,)
        self.c.execute('''UPDATE competitors 
                          SET fname = ?, lname = ?, level = ?, sex = ?, age = ?, 
                          score = ?, r1 = ?, r2 = ?, r3 = ?, r4 = ?, r5 = ?,
                          a1 = ?, a2 = ?, a3 = ?, a4 = ?, a5 = ?
                          WHERE id = ?''', ordered)