#!/usr/bin/python3

import orgproperties as org
import extutil
import json


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

headings = org.parseOrg(org.ORG_PATH)
windows = fetchOpenWindows(headings)

extutil.sendMessage(extutil.encodeMessage(json.dumps(windows)))
