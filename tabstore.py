#!/usr/bin/python3

import os
import sys
import time
import json
import struct

def getMessage():
    raw_message = sys.stdin.buffer.read(4)

    if not raw_message:
        sys.exit(0)

    msg_length = struct.unpack('@I', raw_message)[0]
    message = sys.stdin.buffer.read(msg_length).decode('utf-8')
    return json.loads(message)

def encodeMessage(messageContent):
    encodedContent = json.dumps(messageContent).encode('utf-8')
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}

def sendMessage(encodedMessage):
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()

exec_time = int(time.time())
wait_secs = 10 + (exec_time % 10)
locktime = 0

while os.access('tabstore.lock', os.F_OK):
    locktime = os.stat('tabstore.lock').st_mtime
    #just delete lock if older than 5 minutes
    if locktime + 5*60 < exec_time:
        os.remove('tabstore.lock')
        break
    elif locktime > exec_time:
        sys.exit(0)
    else:
        time.sleep(wait_secs)

with open('tabstore.lock', 'x') as lockfile:
    lockfile.write("")

msg_obj = json.loads(getMessage())
with open('windows.json', 'w') as window_file:
    #window_file.write(str(type(msg_obj)))
    #window_file.write(msg_obj)
    json.dump(msg_obj, window_file, indent=2)

os.remove('tabstore.lock')

sendMessage(encodeMessage('done'))
