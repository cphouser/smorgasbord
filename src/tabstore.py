#!/usr/bin/python3

import os
import sys
import time
import operator
import json

from lib import extutil

exec_time = int(time.time())
wait_secs = 10 + (exec_time % 10)
locktime = 0
MAX_WINDOWS = 100
DATA_PATH = '../data/'
LOCKFILE = os.path.join(DATA_PATH, 'windows.lock')
WINDOWFILE = os.path.join(DATA_PATH, 'windows.json')

while os.access(LOCKFILE, os.F_OK):
    locktime = os.stat(LOCKFILE).st_mtime
    #just delete lock if older than 1 minute
    if locktime + 60 < exec_time:
        os.remove(LOCKFILE)
        break
    elif locktime > exec_time:
        sys.exit(0)
    else:
        time.sleep(wait_secs)

with open(LOCKFILE, 'x') as lockfile:
    lockfile.write("")


msg_obj = json.loads(extutil.getMessage())
window_obj = {}
if os.access(WINDOWFILE, os.F_OK):
    with open(WINDOWFILE, 'r') as window_file:
        old_session = json.load(window_file)
        old_by_url = {window_id: [tab['url'] for tab in old_session[window_id]]
                                  for window_id in old_session}

        window_matches = {}
        new_windows = []
        for win_idx, tabs in msg_obj.items():
            matches = {window_id: len([tab['url'] for tab in tabs
                                       if tab['url'] in old_by_url[window_id]])
                       for window_id in old_by_url}
            #find old window with most matching tabs for each current window
            if matches:
                best_match = max(matches.items(), key=operator.itemgetter(1))[0]
                window_matches[win_idx] = (best_match, matches[best_match])
            else:
                new_windows.append(tabs)
            #with open('test.txt', 'a') as f:
            #    f.write(str(os.getpid()) + str(window_matches) + '\n')

        #assign new window ids by decreasing # of matches
        for win_idx, (matched_win, _) in sorted(window_matches.items(),
                                    key=lambda x: x[1][1], reverse=True):
            match_name, _ = window_matches[win_idx]
            if match_name in window_obj:
                new_windows.append(msg_obj[win_idx])
            else:
                #with open('test.txt', 'a') as f:
                #    f.write(str(os.getpid()) + str(window_obj.keys()) +
                #            str(match_name) + '\n')
                window_obj[match_name] = msg_obj[win_idx]

        while new_windows:
            for i in range(1, MAX_WINDOWS):
                w_name = 'window ' + str(i)
                #with open('test.txt', 'w') as f:

                if w_name not in window_obj:
                    window_obj[w_name] = new_windows.pop()
                    break

else:
    for win_idx, tablist in enumerate(msg_obj.values()):
        window_obj['window ' + str(win_idx)] = tablist


with open(WINDOWFILE, 'w') as window_file:
    #window_file.write(str(type(window_obj)))
    #window_file.write(str(window_obj))
    json.dump(window_obj, window_file, indent=2)


os.remove(LOCKFILE)
extutil.sendMessage(extutil.encodeMessage('done'))
