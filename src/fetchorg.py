#!/usr/bin/python3

import orgproperties as org
import extutil
import json

ORG_PATH = '../../org/brain/webpages.org'

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

headings = org.parseOrg(ORG_PATH)
windows = fetchOpenWindows(headings)

extutil.sendMessage(extutil.encodeMessage(json.dumps(windows)))
