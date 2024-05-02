import os
import sqlite3
from flask import current_app, g

DB_NAME = "database.db"

def init_db():
    DB_PATH = os.path.join(current_app.root_path, DB_NAME)
    if not os.path.exists(DB_PATH):
        db = sqlite3.connect(DB_PATH)
        with current_app.open_resource(f"dbinit.sql", "r") as sql_file:
            db.executescript(sql_file.read())
        db.commit()
        db.close()


def get_db():
    if 'db' not in g:
        init_db()
        DB_PATH = os.path.join(current_app.root_path, DB_NAME)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    
    return g.db


def close_db(e = None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

