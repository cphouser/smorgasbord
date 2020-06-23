"""Routes for parent Flask app."""
from flask import render_template, request, make_response, json
from flask import current_app as app

from datetime import datetime

from . import smorgasbord
from .models import *

@app.route('/')
def home():
    """Landing page."""
    return render_template(
        'index.jinja2',
        title='smorgasbord',
        description='management index',
        template='home-template',
    )

@app.route('/devices/<device>', methods=['PUT'])
def update_device_view(device):
    """update in database the active windows of this device"""
    window_obj = json.loads(request.data.decode('utf-8'))
    windows = {}
    for window in window_obj:
        tabs = {}
        for tab in window['tabs']:
            link_id = smorgasbord.link_id(tab['url'])
            active_ts = datetime.fromtimestamp(tab['lastAccessed'] / 1000)
            tabs[link_id] = (tab['title'], tab['url'], active_ts)
        windows[window['id']] = tabs
    print(windows)
    stored = Device.query.filter_by(id=device).first()
    print(stored, sep='\n')
    return make_response('success', 200)



#def get_windows(win_ids=None, dev_id=None):
#    result = []
#    with app.app_context():
#        cur = get_db().cursor()
#        if win_ids is None and dev_id is None:
#            cur.execute('select * from windows')
#            cols = row.getdescription()
#            return [{cols[i]:row[i] for i in range(cols)} for row in cur]
#
#        elif win_ids is None:
#            cur.execute('select * from windows where dev_id = value(?)',
#                        (dev_id))
#            cols = row.getdescription()
#            return [{cols[i]:row[i] for i in range(cols)} for row in cur]
#
#        else:
#            pass


#@app.route('/import/')
#def db_import():
#    return render_template(
#        'import.jinja2',
#        title='smorgasbord',
#        description='layout import',
#        template='home-template',
#    )
