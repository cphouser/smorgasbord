#!/usr/bin/python3

from lib import orgproperties as org
from lib import extutil
import json

ORG_PATH = '../../org/brain/webpages.org'
JSON_PATH = '../data/windows.json'

def fetchOpenWindows(heading_dict):
    windows = {}
    for heading, properties in heading_dict.items():
        if 'URL' not in properties:
            continue
        elif properties['ACTIVEON'] == 'None':
            continue
        if properties['ACTIVEON'] in windows:
            windows[properties['ACTIVEON']].append(properties['URL'])
        else:
            windows[properties['ACTIVEON']] = [properties['URL']]
    return windows

def fetchWindowJSON(JSON_PATH):
    window_json = {}
    with open(JSON_PATH) as window_file:
        window_json = json.load(window_file)
    return window_json

headings = org.parseOrg(ORG_PATH)
org_windows = fetchOpenWindows(headings)
input = extutil.getMessage()
ff_windows = fetchWindowJSON(JSON_PATH)
extutil.sendMessage(ff_windows)
