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


@app.route('/recent/visits')
def recent_link_visits():
    link_id = request.args.get('link_id', type=str)
    days_back = request.args.get('days_back', type=int)
    time_range = datetime.now() - timedelta(days=days_back)
    recent_visits = (db.session.query(Visit)
        .filter(Visit.time > time_range.strftime('%Y-%m-%d %H:%M:%S'))
        .filter(Visit.link_id==link_id)
        .order_by(db.desc(Visit.time)))
    result = '\n'.join([str(visit) for visit in recent_visits])
    #print(link_id, days_back)
    #print(list(recent_visits.all()))
    return json.dumps(dict(link_id=link_id, result=result))


@app.route('/link/tags')
def show_link_tags():
    link_id = request.args.get('link_id', type=str)
    link_tags = Link.query.filter_by(id=link_id).first().tags
    tag_strings = []
    for tag in link_tags:
        tag_str = tag.id
        while (tag.parent):
            tag_str = tag_str + ' \u2194 ' + tag.parent.id
            tag = tag.parent
        tag_strings.append(tag_str)

    result = '\n'.join(tag_strings)
    return json.dumps(dict(link_id=link_id, result=result))


@app.route('/link/<link_id>', methods=['GET'])
def get_link_data(link_id):
    link = Link.query.filter_by(id=link_id).first()
    return json.dumps(dict(link_id=link_id, title=link.title,
                           desc=link.description, match=link.match,
                           parent=link.parent))


@app.route('/tag/<tag_id>', methods=['PUT'])
def add_tag(tag_id):
    #print(tag_id)
    if not tag_id == tag_id.strip().lower().replace(' ', '_'):
        return make_response('tag id must be lowercase with no spaces)', 400);
    tag = Tag(id=tag_id)
    db.session.add(tag)
    db.session.commit()
    return make_response('success', 200)


@app.route('/links/tags', methods=['POST'])
def add_tag_links():
    link_ids = json.loads(request.form.get('link_ids'))
    tag_id = request.form.get('tag')
    tag = Tag.query.filter_by(id=tag_id).first()
    for link_id in link_ids:
        link = Link.query.filter_by(id=link_id).first()
        link.tags.append(tag)
        db.session.add(link)
    db.session.commit()
    return make_response('ok', 200)


@app.route('/links/tags', methods=['DELETE'])
def remove_tag_links():
    tag_id = request.form.get('tag')
    link_ids = json.loads(request.form.get('link_ids'))
    tag = Tag.query.filter_by(id=tag_id).first()
    for link_id in link_ids:
        link = Link.query.filter_by(id=link_id).first()
        link.tags.remove(tag)
    db.session.commit()


@app.route('/links/tags', methods=['GET'])
def show_tag_intersection():
    link_ids = json.loads(request.args.get('link_ids'))
    link_tags = set(Link.query.filter_by(id=link_ids.pop()).first().tags)
    for link_id in link_ids:
        link_tags = link_tags.intersection(set(
            Link.query.filter_by(id=link_id).first().tags))
    result = [tag.id for tag in link_tags]
    return json.dumps(dict(tags=result))


@app.route('/tags/list')
def list_tags_tree():
    def rec_populate(tag, depth=0, end=False):
        if end:
            tag_list.append(dict(pre='\u2503' * (depth - 1) + '\u2517 ',
                                 id=tag.id))
        elif depth:
            tag_list.append(dict(pre='\u2503' * (depth - 1) + '\u2523 ',
                                 id=tag.id))
        else:
            tag_list.append(dict(pre='', id=tag.id))
        children = Tag.query.filter_by(parent=tag.id).order_by(Tag.id).all()
        last = None
        if children:
            last = children.pop()
        for child in children:
            rec_populate(child, depth + 1)
        if last:
            rec_populate(last, depth + 1, True)
    tag_list = []
    root_tags = Tag.query.filter_by(parent=None).order_by(Tag.id)
    for tag in root_tags:
        rec_populate(tag)
    return json.dumps(dict(tags=tag_list))


@app.route('/recent')
def show_recent_links():
    days_back = request.args.get('days', default=30, type=int)
    day_str = 'day' if days_back == 1 else str(days_back) + 'days'
    time_range = datetime.now() - timedelta(days=days_back)
    recent_visits = (db.session.query(
        db.func.max(Visit.time), Link, db.func.count('*'))
        .filter(Visit.time > time_range.strftime('%Y-%m-%d %H:%M:%S'))
        .filter(Visit.link_id==Link.id)
        .group_by(Visit.link_id)
        .order_by(db.desc(db.func.max(Visit.time))))
    link_table = []
    for recent_ts, link, visit_count in recent_visits:
        tags = [tag.id for tag in link.tags] if len(link.tags) else ["UNTAGGED"]
        row = dict(id=link.id, time=recent_ts, count=visit_count,
                   title=link.title, url=link.url, tags=", ".join(tags))
        link_table.append(row)
    columns = ['Select', 'Last Visit', '#Visits', 'Title', 'URL', 'Tags']
    return render_template('recent.jinja2',
                           title='smorgasbord',
                           description='recently visited links',
                           columns=columns,
                           recent_links=link_table,
                           days_back=days_back,
                           template='table-view')
