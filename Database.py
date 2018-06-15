import sqlite3


# database containing all the competitors and their information
# accessed by nearly every class
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
        self.c.executemany('''INSERT INTO competitors (id, fname, lname, level, sex, age, score, r1, r2, r3, r4, r5, a1, a2, a3, a4, a5)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', rows)

    def delete_row(self, id):
        self.c.execute('''DELETE FROM competitors WHERE id = ?''', (id,))

    def delete_all(self):
        self.c.execute('DELETE FROM competitors')

    def get_all(self):
        self.c.execute('SELECT * FROM competitors ORDER BY lname COLLATE NOCASE')
        return self.c.fetchall()

    def get_row(self, id):
        self.c.execute('''SELECT * FROM competitors WHERE id = ?''', (id,))
        return self.c.fetchone()

    def get_specific_rows_by_score(self, **kwargs):  # orders by score by default
        attributes = ('id', 'fname', 'lname', 'level', 'sex', 'age', 'score',
                      'r1', 'r2', 'r3', 'r4', 'r5', 'a1', 'a2', 'a3', 'a4', 'a5')

        execstring = 'SELECT id, fname, lname, score FROM competitors'
        areAttributes=False

        for i, k in enumerate(kwargs.keys()):
            if i == 0:
                execstring += ' WHERE'
                areAttributes = True
            if k in ('id', 'age', 'score', 'r1', 'r2', 'r3', 'r4', 'r5', 'a1', 'a2', 'a3', 'a4', 'a5'):
                execstring += ' {} = {} AND'.format(k, kwargs[k])
            elif k in ('fname', 'lname', 'level', 'sex'):
                execstring += ' {} = \'{}\' AND'.format(k, kwargs[k])
        if areAttributes:
            execstring = execstring[:-4] + ' ORDER BY score DESC'

        self.c.execute(execstring)
        return self.c.fetchall()

    def get_specific(self, pattern):
        self.c.execute('''SELECT * from competitors WHERE fname LIKE ? OR 
                                                          lname LIKE ? OR
                                                          id LIKE ? OR 
                                                          sex LIKE ? OR 
                                                          level LIKE ?''',
                       (pattern+'%', pattern+'%', pattern+'%', pattern+'%', pattern+'%'))
        return self.c.fetchall()

    def update_row(self, id, info):
        ordered = info + (id,)
        self.c.execute('''UPDATE competitors 
                          SET fname = ?, lname = ?, level = ?, sex = ?, age = ?, 
                          score = ?, r1 = ?, r2 = ?, r3 = ?, r4 = ?, r5 = ?,
                          a1 = ?, a2 = ?, a3 = ?, a4 = ?, a5 = ?
                          WHERE id = ?''', ordered)
