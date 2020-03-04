#!/usr/bin/python3

import os
import sys
import time
import operator
import json

from lib import extutil

MAX_WINDOWS = 100
DATA_PATH = '../data/'
LOCKFILE = os.path.join(DATA_PATH, 'windows.lock')
WINDOWFILE = os.path.join(DATA_PATH, 'windows.json')

exec_time = int(time.time())
wait_secs = 10 + (exec_time % 10)
locktime = 0

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

msg_obj = extutil.getMessage()
window_obj = {}

with open(WINDOWFILE, 'w') as window_file:
    json.dump(msg_obj, window_file, indent=2)


os.remove(LOCKFILE)
extutil.sendMessage('done')
