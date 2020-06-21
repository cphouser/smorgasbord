"""Routes for parent Flask app."""
from flask import render_template, request, make_response, json
from flask import current_app as app

from datetime import datetime

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
    windows = json.loads(request.data.decode('utf-8'))
    for window in windows:
        print(window['id'])
        for tab in window['tabs']:
            print([tab.keys()])
    return make_response('success', 200)





#@app.route('/import/')
#def db_import():
#    return render_template(
#        'import.jinja2',
#        title='smorgasbord',
#        description='layout import',
#        template='home-template',
#    )
