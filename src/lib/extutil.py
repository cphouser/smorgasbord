
import sys
import json
import struct

def getMessage():
    """
    Load an encoded JSON message from stdin and return python object.
    """
    raw_message = sys.stdin.buffer.read(4)

    if not raw_message:
        sys.exit(0)

    msg_length = struct.unpack('@I', raw_message)[0]
    message = sys.stdin.buffer.read(msg_length).decode('utf-8')
    return json.loads(message)


def sendMessage(message):
    """
    Send a serialized JSON message of object "message" to stdout.
    """
    def encodeMessage(messageContent):
        encodedContent = json.dumps(messageContent).encode('utf-8')
        encodedLength = struct.pack('@I', len(encodedContent))
        return {'length': encodedLength, 'content': encodedContent}
    encodedMessage = encodeMessage(json.dumps(message))
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()
