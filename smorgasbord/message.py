
import random
from .models import *
#from sqlalchemy import in_
from flask import json
from .models import *

class Msg:
    """a message showing the changes to make during the next browser update

    the message is structured in the following way:

    message: {
        tab {
            url: the url for the tab
            id: if specified, the window browser id (bid) to move the tab from
        }
        window {
            id: the id for the window if it exists or a placeholder
            bid: the bid for the window if it exists
            tag: a tag_id which if specified sorts any added links with that
                tag into this window
            tabs: [list of tabs]
        }
        open: [list of new windows to open with corresponding tabs]
        change: [list of windows with corresponding tabs to add]
        close: [list of windows with corresponding tabs to close.
                if the list of tabs is null, close whole window]
    }

    Attributes:
        device:
        p_open, p_change, p_close: the lists as described in the above
            message form

    """
    def __init__(self, device_id, p_open=[], p_change=[], p_close=[]):
        device = Device.query.filter_by(id=device_id).first()
        if not device:
            return None
        self.device = device
        self.p_open = p_open
        self.p_change = p_change
        self.p_close = p_close

    def openmove_new_win(self, linkid_list, tag_id=None):
        suffix = format(random.randrange(4096), 'x').rjust(3, '0')
        window = dict(id='_OPEN_' + suffix, tag=tag_id, tabs=[])
        #if tag_id:
        #    window['tag'] = tag_id
        #window['tabs'] = []
        #window['id'] = '_OPEN_' + suffix
        window_ids = [win.id for win in self.device.windows]
        for link_id in linkid_list:
            tab = {}
            windowlink = WindowLinks.query.filter(
                WindowLinks.win_id.in_(window_ids)).filter_by(
                    link_id=link_id).first()
            if windowlink:
                tab['id'] = Window.query.filter_by(id=windowlink.win_id).first().bid
                tab['url'] = windowlink.url
            else:
                tab['url'] = Link.query.filter_by(id=link_id).first().url
            window['tabs'] += [tab]
        self.p_open += [window]

    def openmove_cur_win(self, linkid_list, win_id, tag_id=None):
        bid = Window.query.filter_by(id=win_id).first().bid
        window = dict(id=win_id, bid=bid, tag=tag_id, tabs=[])
        window_ids = [win.id for win in self.device.windows]
        for link_id in linkid_list:
            tab = {}
            windowlink = WindowLinks.query.filter(
                WindowLinks.win_id.in_(window_ids)).filter_by(
                    link_id=link_id).first()
            if windowlink:
                tab['id'] = Window.query.filter_by(id=windowlink.win_id).first().bid
                tab['url'] = windowlink.url
            else:
                tab['url'] = Link.query.filter_by(id=link_id).first().url
            window['tabs'] += [tab]
        self.p_change += [window]

    def close_win(self, linkid_list, win_id):
        bid = Window.query.filter_by(id=win_id).first().bid
        window = dict(id=win_id, bid=bid)
        if linkid_list is not None:
            window['tabs'] = []
            for link_id in linkid_list:
                windowlink = WindowLinks.query.filter_by(link_id=link_id,
                                                         win_id=win_id).first()
                if windowlink:
                    window['tabs'] += [dict(url=windowlink.url)]
        else:
            window['tabs'] = None
        self.p_close += [window]

    def clear(self):
        for p_list in (self.p_open, self.p_close, self.p_change):
            p_list.clear()

    def __str__(self):
        return json.dumps(dict(p_open=self.p_open,
                               p_change=self.p_change,
                               p_close=self.p_close))
