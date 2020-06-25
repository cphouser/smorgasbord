"""Routes for parent Flask app."""
from flask import render_template, request, make_response, json
from flask import current_app as app


from datetime import datetime, timedelta

from . import smorgasbord
from .models import *
from .devices import *

@app.route('/')
def home():
    """Landing page."""
    return render_template('index.jinja2',
                           title='smorgasbord',
                           description='management index',
                           template='home-template')


@app.route('/recent')
def show_recent_links():
    days_back = 30
    day_str = 'day' if days_back == 1 else str(days_back) + 'days'
    time_range = datetime.now() - timedelta(days=days_back)
    print(time_range)
    recent_visits = (db.session.query(
        db.func.max(Visit.time), Link, db.func.count('*'))
        .filter(Visit.time > time_range.strftime('%Y-%m-%d %H:%M:%S'))
        .filter(Visit.link_id==Link.id)
        .group_by(Visit.link_id)
        .order_by(db.desc(db.func.max(Visit.time))))
    link_table = []
    for recent_ts, link, visit_count in recent_visits:
        tags = [tag.id for tag in link.tags]
        row = dict(id=link.id, time=recent_ts, count=visit_count,
                   url=link.url, title=link.title, tags=", ".join(tags))
        link_table.append(row)
    columns = dict(time='Last Visit', count='#Visits in last '+day_str,
                   url='URL', title='Title', tags='Tags')
        #print(recent_ts, link, visit_count)
    #dummy_list = [dict(id='asf', url='sdf', title='sddd', tags="ddddfd"),
    #              dict(id='af', url='df', title='sdd', tags="dddfd"),
    #              dict(id='f', url='d', title='sd', tags="dfd")]
    return render_template('recent.jinja2',
                           title='smorgasbord',
                           description='recently visited links',
                           columns=columns,
                           recent_links=link_table,
                           template='home-template')

