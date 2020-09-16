"""Routes for parent Flask app."""
from flask import render_template, request, make_response, json
from flask import current_app as app


from datetime import datetime, timedelta

from . import smorgasbord
from . import message
from .models import *
from .devices import *

@app.route('/')
def home():
    """Landing page."""
    return render_template('index.jinja2',
                           title='smorgasbord',
                           subtitle='management index')

@app.route('/smorgasbord')
def awake():
    return json.dumps({'status': 'online',
                       'version': '0.1',
                       'time': str(datetime.now())}), 200

@app.route('/recent/visits')
def recent_link_visits():
    """retrieve dates of all visits to a link in the specified days.

    Args:
        link_id: the link_id to retrieve visits for.
        days_back: the number of days back to look.

    Returns:
        A serialized dict containing the link_id and associated result.

        link_id: the link_id for the retrieved visits.
        result: a newline separated list of visit timestamps.
    """
    link_id = request.args.get('link_id', type=str)
    days_back = request.args.get('days_back', type=int)
    time_range = datetime.now() - timedelta(days=days_back)
    recent_visits = (db.session.query(Visit)
        .filter(Visit.time > time_range.strftime('%Y-%m-%d %H:%M:%S'))
        .filter(Visit.link_id==link_id)
        .order_by(db.desc(Visit.time)))
    result = '\n'.join([str(visit) for visit in recent_visits])
    return json.dumps(dict(link_id=link_id, result=result))


@app.route('/link')
def find_url():
    link_url = request.args.get('url', type=str)
    link_id = smorgasbord.link_id(link_url)
    if Link.query.filter_by(id=link_id).first() is None:
        #check matches
        status = 'unsaved'
    else:
        status = 'saved'
    return json.dumps(dict(link_id=link_id, status=status))


@app.route('/link', methods=['POST'])
def add_url():
    data = json.loads(request.data)
    link_url = data.get('url')
    link_id = smorgasbord.link_id(link_url)
    if Link.query.filter_by(id=link_id).first() is not None:
        return make_response('Link Already Exists', 409);

    tag = Tag.query.filter_by(id=data.get('tag')).first()
    if tag is None:
        return make_response('Tag Does Not Exist', 404);

    link = Link(id=link_id, title=data.get('title'), url=link_url)
    link.tags.append(tag)
    db.session.add(link)
    db.session.commit()
    return json.dumps(dict(link_id=link_id)), 201


@app.route('/link/tags')
def show_link_tags():
    """Retrieve a list of all tags associated with a specified link.

    If a tag has a parent tag, return the tag concatenated with a list
    of its ancestors, separated by an arrow character.

    Args:
        link_id: the link_id to find tags for.
        format: whether for format the result as a string

    Returns:
        A serialized dict containing the link_id and associated result.

        link_id: the link_id for the returned tag list
        result: a list of the tags the link_id is associated with.
    """
    link_id = request.args.get('link_id', type=str)
    link_tags = Link.query.filter_by(id=link_id).first().tags
    tag_strings = []
    for tag in link_tags:
        tag_str = tag.id
        while (tag.parent):
            tag_str = tag_str + ' \u2b95 ' + tag.parent
            tag = Tag.query.filter_by(id=tag.parent).first()
        tag_strings.append(tag_str)
    if request.args.get('format', type=bool):
        result = '\n'.join(tag_strings)
    else:
        result = {t.id: s for t, s in zip(link_tags, tag_strings)}
    return json.dumps(dict(link_id=link_id, result=result))


@app.route('/link/<link_id>', methods=['GET'])
def get_link_data(link_id):
    """Retrieve every property of the specified link_id

    Args:
        link_id: the link_id to find tags for.

    Returns:
        A serialized dict containing the link_id and associated result.

        link_id: the link_id for the returned data.
        title: the link title.
        url: the link url.
        desc: the link description.
        match: the associated match string for the link.
        parent: the parent link_id for the link.
    """
    link = Link.query.filter_by(id=link_id).first()
    return json.dumps(dict(link_id=link_id, title=link.title,
                           url=link.url, desc=link.description,
                           match=link.match, parent=link.parent))


@app.route('/link/<link_id>', methods=['DELETE'])
def remove_link(link_id):
    """delete the specified link_id from the database.

    Args:
        link_id: the link_id to remove.

    Returns:
        An HTTP success response.
    """
    link = Link.query.filter_by(id=link_id).first()
    db.session.delete(link)
    db.session.commit()
    return make_response('success', 200)


@app.route('/tag/<tag_id>', methods=['PUT'])
def add_tag(tag_id):
    """Add the specified tag to the database.

    The format for tag ids should be lowercase ASCII without spaces.

    Args:
        tag_id: the tag to add.
        an optional JSON body with a parent tag id and/or a tag description

    Returns:
        An HTTP success response.
    """
    if not tag_id == tag_id.strip().lower().replace(' ', '_'):
        return make_response('tag id must be lowercase with no spaces', 400);
    tag = Tag(id=tag_id)
    data = json.loads(request.data)
    parent_id = data.get('parent')
    if parent_id:
        if not Tag.query.filter_by(id=parent_id).first():
            return make_response('parent tag id is not valid', 400);
        tag.parent = parent_id

    tag_desc = data.get('desc')
    if tag_desc:
        tag.description = tag_desc

    db.session.add(tag)
    db.session.commit()
    return make_response('success', 200)


@app.route('/links/tags', methods=['POST'])
def add_tag_links():
    """Add a connection for each link to the specified tag.

    links and tag must already be in database. If the specified tag is not
    found the action fails. If a specified link is not found in the saved or
    active links the entry is skipped silently. If a link is only found in the
    set of active links it is saved.

    Args:
        tag_id: the tag to add a connection to.
        link_ids: a list of link ids to connect to the tag.

    Returns:
        An HTTP success response.
    """
    link_ids = json.loads(request.form.get('link_ids'))
    tag_id = request.form.get('tag')
    tag = Tag.query.filter_by(id=tag_id).first()
    for link_id in link_ids:
        link = Link.query.filter_by(id=link_id).first()
        if link is None:
            wl = WindowLinks.query.filter_by(link_id=link_id).first()
            if wl is None:
                continue
            link = Link(id=link_id, title=wl.title, url=wl.url)
            db.session.add(link)
        link.tags.append(tag)
        db.session.add(link)
    db.session.commit()
    return make_response('success', 200)


@app.route('/links/tags', methods=['DELETE'])
def remove_tag_links():
    """removes a connection for each link to the specified tag.

    Links and tag must already be in database. If the specified tag
    or any link is not found the action fails.

    Args:
        tag_id: the tag to remove a connection to.

    Returns:
        An HTTP success response.
    """
    tag_id = request.form.get('tag')
    link_ids = json.loads(request.form.get('link_ids'))
    tag = Tag.query.filter_by(id=tag_id).first()
    for link_id in link_ids:
        link = Link.query.filter_by(id=link_id).first()
        link.tags.remove(tag)
    db.session.commit()
    return make_response('success', 200)


@app.route('/links/tags', methods=['GET'])
def show_tag_intersection():
    link_ids = json.loads(request.args.get('link_ids'))
    first_id = Link.query.filter_by(id=link_ids.pop()).first()
    if not first_id:
        return json.dumps(dict(tags=[]))
    link_tags = set(first_id.tags)
    for link_id in link_ids:
        link = Link.query.filter_by(id=link_id).first()
        if not link:
            return json.dumps(dict(tags=[]))
        link_tags = link_tags.intersection(set(link.tags))
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


def tag_dict():
    def rec_populate(tag, parent_dict):
        parent_dict[tag.id] = {}
        children = Tag.query.filter_by(parent=tag.id).order_by(Tag.id)
        for child in children:
            rec_populate(child, parent_dict[tag.id])

    root_tags = Tag.query.filter_by(parent=None).order_by(Tag.id)
    tag_dict = {}
    for tag in root_tags:
        rec_populate(tag, tag_dict)
    return tag_dict


@app.route('/recent/')
def show_recent_links():
    days_back = request.args.get('days', default=30, type=int)
    day_str = 'day' if days_back == 1 else str(days_back) + ' days'
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
                           title='recent visits',
                           columns=columns,
                           recent_links=link_table,
                           days_back=days_back,
                           subtitle='Links visited in last '+day_str)


@app.route('/active/')
def show_active():
    windows = Window.query.all()
    print(windows)
    win_tables = {}
    for window in windows:
        links = window.links
        devices = ', '.join([device.id for device in window.devices])
        link_list = []
        for link in links:
            linkitem = Link.query.filter_by(id=link.link_id).first()
            if linkitem:
                tag_strs = [tag.id for tag in linkitem.tags]
                tags = ' ,'.join(tag_strs) if tag_strs else 'UNTAGGED'
            else:
                tags = ''
            link_list.append(dict(id=link.link_id, time=link.time,
                                  url=link.url, duration=link.duration,
                                  title=link.title, tags=tags))
        win_tables[window.id] = dict(count=len(links), devices=devices,
                                     links=link_list)
    columns = ['Select', 'Opened Since', 'Opened For', 'Title', 'URL', 'Tags']
    return render_template('active.jinja2',
                           title='active windows',
                           columns=columns,
                           windows=win_tables,
                           subtitle='Links currently opened')

@app.route('/tags/')
def browse_tags():
    def recursive_format(tag_dict, nested_summary):
        for tag_id, children in tag_dict.items():
            tag_info = tag_summary(tag_id)
            tag_info['children'] = []
            if children:
                recursive_format(children, tag_info['children'])
            nested_summary += [tag_info]
    tags = tag_dict()
    summary = []
    recursive_format(tags, summary)
    return render_template('tags.jinja2', title='browse tags',
                           tags=summary)


def tag_summary(tag_id):
    tag = Tag.query.filter_by(id=tag_id).first()
    child_count = len(tag.children)
    link_count = len(tag.links)
    return dict(id=tag_id, desc=tag.description, child_count=child_count,
                link_count=link_count)
