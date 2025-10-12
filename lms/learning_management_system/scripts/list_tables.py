import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
print('DB path:', DB)
print('Exists:', os.path.exists(DB))
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cur.fetchall()]
print('Tables:')
for t in tables:
    print(' -', t)
conn.close()
