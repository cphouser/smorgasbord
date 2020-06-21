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

def get_windows(win_ids=None, dev_id=None):
    result = []
    cur = get_db().cursor()
    if win_ids is None and dev_id is None:
        cur.execute('select * from windows')
        cols = row.getdescription()
        return [{cols[i]:row[i] for i in range(cols)} for row in cur]

    elif win_ids is None:
        cur.execute('select * from windows where dev_id = value(?)',
                    (dev_id))
        cols = row.getdescription()
        return [{cols[i]:row[i] for i in range(cols)} for row in cur]

    else:
        pass
