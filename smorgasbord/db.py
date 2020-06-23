from flask import g
from flask import current_app as app
import apsw

DATABASE = 'data/smorgasbord.db'

def get_db():
    db = get_attr(g, '_database', None)
    if db is None:
        db = g._database = aspw.Connection(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

