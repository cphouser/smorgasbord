 
from flask import request, make_response, json
from flask import current_app as app
from datetime import datetime, timedelta
from pytimeparse import parse as to_seconds
from . import smorgasbord
from .models import *

from .message import *


@app.route('/windows/', methods=['GET'])
def retrieve_window_list():
    windows = [window.id for window in Window.query]
    return json.dumps(dict(windows=windows))

@app.route('/devices/', methods=['GET'])
def retrieve_device_list():
    win_id = request.args.get('win_id', type=str)
    if win_id:
        win = Window.query.filter_by(id=win_id).first()
        devices = [dev.id for dev in Device.query.filter(Device.windows.contains(win))]
    else:
        devices = [dev.id for dev in Device.query]

    return json.dumps(dict(devices=devices))

@app.route('/devices/messages', methods=['GET'])
def retrieve_all_messages():
    messages = {}
    indent = 0
    for dev in Device.query:
        if dev.message:
            messages[dev.id] = json.dumps(json.loads(dev.message), indent=2)
    return json.dumps(dict(result=messages))

@app.route('/devices/<device>/messages', methods=['GET'])
def retrieve_device_message(device):
    dev = Device.query.filter_by(id=device).first()
    if dev and dev.message:
        message = dev.message
        dev.message = ''
    else:
        message = json.dumps(dict())
    db.session.commit()
    return json.dumps(message)

@app.route('/devices/<device>/messages', methods=['POST'])
def add_device_message(device):
    dev = Device.query.filter_by(id=device).first()
    msg = request.form.get('message')
    if dev and msg:
        tag = request.form.get('tag')
        link_id_obj = request.form.get('link_ids')
        link_ids = json.loads(link_id_obj) if link_id_obj else None
        message = Msg(device)
        message.clear()
        #TODO merge the messages
        if dev.message:
            pass
        else:
            pass
        if msg == 'open':
            message.openmove_new_win(link_ids, tag)
        elif msg == 'change':
            win_id = request.form.get('win_id')
            message.openmove_cur_win(link_ids, win_id, tag)
        elif msg == 'close':
            win_id = request.form.get('win_id')
            message.close_win(link_ids, win_id)
        dev.message = str(message)
        db.session.commit()
        return make_response('success', 200)
    else:
        return make_response('device {device} or message {msg} invalid', 400)

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

    stored = Device.query.filter_by(id=device).first()
    if stored:
        # separate new windows from old windows from dead windows
        win_diff = sort_windows(stored, windows)
    else:
        # declare new device from route and open windows as new
        new_device = Device(id=device)
        db.session.add(new_device)
        db.session.commit()
        win_diff = dict(add=list(windows.keys()), remove=[], update=[])
        stored = new_device

    for window_bid in win_diff['add']:
        tabs = windows[window_bid]
        add_window(window_bid, stored, tabs)

    for window_id in win_diff['remove']:
        remove_window(window_id)

    for id, bid in win_diff['update']:
        tabs = windows[bid]
        update_window(id, bid, stored, tabs)

    return make_response('success', 200)


def add_windowlink(win_id, link_id, title, url, last_access):
    """
    adds a link to the window_links table, adds to links table if absent

    initializes duration to 0 and time to last access.
    """
    time_str = last_access.strftime('%Y-%m-%d %H:%M:%S')
    wl = WindowLinks(win_id=win_id, link_id=link_id, time=time_str, url=url,
                     title=title, duration='0:00:00:00')
    
    db.session.add(wl)
    db.session.commit()


def update_windowlink(win_link, last_access):
    """update the duration property of a window link by a last_access ts"""
    def pad(int_val):
        return str(int_val).rjust(2, '0')
    init_time = datetime.strptime(win_link.time, '%Y-%m-%d %H:%M:%S')
    duration = last_access - init_time
    dur_str = ':'.join((str(duration.days), pad(duration.seconds // 3600),
                        pad((duration.seconds % 3600) // 60),
                        pad(((duration.seconds % 3600) % 60 % 60))))
    win_link.duration = dur_str
    db.session.commit()


def remove_windowlink(win_link):
    """
    removes link from window_links and adds corresponding entry to visits.
    """

    #print(win_link.duration, to_seconds(win_link.duration))
    if Link.query.filter_by(id=win_link.link_id):
        #print('****')
        duplicate = Visit.query.filter_by(link_id=win_link.link_id, time=win_link.time).first()
        if duplicate:
            if to_seconds(win_link.duration):
                duplicate.duration = win_link.duration
        else:
            visit = Visit(link_id=win_link.link_id, time=win_link.time,
                          duration=(win_link.duration
                                    if to_seconds(win_link.duration) else None))
            db.session.add(visit)
            db.session.commit()
    db.session.delete(win_link)
    db.session.commit()


def update_window(id, bid, device, b_tabs):
    window = Window.query.filter_by(id=id).first()
    if bid != window.bid:
        print("update bid")
        window.bid = bid
        db.session.commit()
        #update = Window.update().where(Window.c.id == id).values(bid=bid)
        #db.engine.execute(update)
    db_tabs = WindowLinks.query.filter_by(win_id=id)
    for window_link in db_tabs:
        #check if window_link still exists (multiple instances of this function running?)
        if window_link and window_link.link_id in b_tabs:
            update_windowlink(window_link, b_tabs[window_link.link_id][2])
            del b_tabs[window_link.link_id]
        #check if window_link still exists (multiple instances of this function running?)
        elif window_link:
            remove_windowlink(window_link)
    for tab, (title, url, last_access) in b_tabs.items():
        add_windowlink(id, tab, title, url, last_access)


def add_window(window_bid, device, tabs):
    """
    add window to database, initialize all open links in window_links table

    parameters: bid of Window; parent device object of window;
        dict of open tabs, keyed by link_id.
    generates a window_id based on earliest access data of child open tabs.
    """
    earliest = min([tab_data[2] for tab_data in tabs.values()])
    window_id = smorgasbord.window_id(earliest)
    new_window = Window(bid=window_bid, id=window_id)
    new_window.devices.append(device)
    db.session.add(new_window)
    db.session.commit()
    for link_id, (title, url, last_access) in tabs.items():
        add_windowlink(window_id, link_id, title, url, last_access)


def remove_window(window_id):
    """
    remove window from database, add all previously open links to visits

    parameters: id of Window
    """
    links = WindowLinks.query.filter_by(win_id=window_id)
    for link in links:
        remove_windowlink(link)
    window = Window.query.filter_by(id=window_id).first()
    db.session.delete(window)
    db.session.commit()


def sort_windows(device, windows):
    """
    matches browser windows to windows associated with the specified device

    browser windows are passed as a dict keyed by browser id where each
    value is a dict keyed by link id. device is passed as Device object.
    returns a dict with three entries on keys: add, remove, update.
    add is a list of bids to add to the database.
    remove is a list of window ids to remove from the database.
    update is a list of tuples (id, bid) to be updated in the database.
    """
    def link_difference(resp_links, db_win):
        diff = 0
        for win_links in db_win:
            if win_links.link_id in resp_links:
                resp_links.remove(win_links.link_id)
            else:
                diff = diff + 1
        return max([diff, len(resp_links)])

    window_update = dict(add=list(windows.keys()),
                         remove=[win.id for win in device.windows],
                         update=[])
    # find all matching stored windows by browser_id
    db_win_list = [win.id for win in device.windows]
    for win, tabs in windows.items():
        #print(win, tabs.keys())
        db_matched_windows = Window.query.filter_by(bid=win).all()
        comparison = {}
        for db_window in db_matched_windows:
            win_links = WindowLinks.query.filter_by(win_id=db_window.id).all()
            if len(win_links):
                comparison[db_window.id] = link_difference(list(tabs.keys()),
                                                           win_links)
        if len(comparison):
            #print('--', comparison)
            #print('--', window_update)
            best_match = min(comparison, key=comparison.get)
            #print('--', best_match)
            window_update['update'].append((best_match, win))
            window_update['add'].remove(win)
            window_update['remove'].remove(best_match)

    # find tab difference for each stored window for each browser window
    comparisons = {}
    for bid in window_update['add']:
        b_tabs = windows[bid]
        comparison = {}
        for db_id in window_update['remove']:
            win_links = WindowLinks.query.filter_by(win_id=db_id).all()
            if len(win_links):
                comparison[db_id] = link_difference(list(b_tabs.keys()),
                                                    win_links)
        if len(comparison):
            best_match = min(comparison, key=comparison.get)
            comparisons[bid] = ((best_match, comparison[best_match]),
                                 comparison)
    # link all comparable update window bids with db window ids by best match
    while(len(comparisons)):
        best_window = min(comparisons, key=(lambda x: comparisons[x][0][1]))
        matches = comparisons[best_window][1]
        best_match = min(matches, key=matches.get)
        if best_match in window_update['remove']:
            window_update['add'].remove(best_window)
            window_update['remove'].remove(best_match)
            window_update['update'].append((best_match, best_window))
            del comparisons[best_window]
        else:
            del matches[best_match]
            if len(matches):
                next_best_match = min(matches, key=matches.get)
                comparisons[best_window] = ((next_best_match,
                                             matches[next_best_match]),
                                            matches)
            else:
                del comparisons[best_window]

    #print(*window_update.items(), sep='\n')
    return window_update
