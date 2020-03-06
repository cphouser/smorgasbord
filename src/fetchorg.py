#!/usr/bin/python3

from lib import orgproperties as org
from lib import extutil
from lib import window
import json

FIELDS = ['MATCH']
ORG_PATH = '../../org/brain/webpages.org'
JSON_PATH = '../data/windows.json'

def fetchOpenWindows(heading_dict):
    windows = {}
    for heading_str, entry in heading_dict.items():
        if 'URL' not in entry['properties']:
            continue
        elif entry['tags'] == []:
            continue

        properties = entry['properties']
        url = properties['URL']
        tags = entry['tags']
        item = {}
        head_idx = heading_str.rfind('/')
        item['title'] = heading_str[head_idx + 1:]
        item['parent'] = heading_str[heading_str.rfind('/',0 , head_idx - 1) + 1
                                     :head_idx]
        item['stored'] = True
        for field in FIELDS:
            if field in properties:
                item[field.lower()] = properties[field]

        for tag in tags:
            if tag == '': continue
            if tag not in windows:
                windows[tag] = {}
            windows[tag][url] = item
    return windows

def fetchWindowJSON(JSON_PATH):
    window_json = {}
    with open(JSON_PATH) as window_file:
        window_json = json.load(window_file)
    return window_json

if __name__ == '__main__':
    headings = org.parseOrg(ORG_PATH)
    org_windows = window.initFromOrg(fetchOpenWindows(headings))
    ff_windows = window.Windows(fetchWindowJSON(JSON_PATH))
    reload_scratch = extutil.getMessage()
    window_delta = window.windowDelta(ff_windows, org_windows, reload_scratch)

    extutil.sendMessage(window_delta.asDict())
