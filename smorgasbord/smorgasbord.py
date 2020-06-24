import zlib
import random
from datetime import datetime


def link_id(url):
    chk_str = format(zlib.crc32(url.encode('ascii')), 'x')
    start_idx = url.find(':') + 1
    while(url[start_idx] == '/'):
        start_idx = start_idx + 1
    end_idx = url.find('/', start_idx)
    return chk_str.rjust(8, '0') + url[start_idx:end_idx].replace('.', '')

def window_id(timestamp):
    suffix = format(random.randrange(4096), 'x').rjust(3, '0')
    dt_str = timestamp.strftime('%y-%m-%d_%H:%M_')
    return dt_str + suffix
