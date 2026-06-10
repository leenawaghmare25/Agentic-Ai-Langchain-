import sqlite3
conn = sqlite3.connect('database.db')
conn.execute('''CREATE TABLE users
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
         name text NOT NULL, 
         email text NOT NULL)''')
conn.close()