import mysql.connector
from flask import g

DB_CONFIG = {
    'host': 'sql100.infinityfree.com',   # તમારા InfinityFree panelમાં દેખાતું host
    'user': 'if0_xxxxxx',               # તમારો MySQL username
    'password': 'your_mysql_password',  # તમારો MySQL password
    'database': 'if0_xxxxxx_marutibilling'  # તમારું DB name
}

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
