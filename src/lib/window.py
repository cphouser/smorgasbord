import sys

class Windows:
    windows = {}
    def __init__(self, windowDict={}):
        for ffid, window in windowDict.items():
            self.windows[(ffid, window['owid'])] = window['tabs']

    def inDict(self, ffid='', owid=''):
        if not ffid:
            if any(o_id == owid for (f_id, o_id) in self.windows):
                return True
            else: return False

        if not owid:
            if any(f_id == ffid for (f_id, o_id) in self.windows):
                return True
            else: return False

        if (ffid, owid) in self.windows:
            return True
        else:
            return False

    def asDict(self, key=None):
        returnDict = {}
        for ((ffid, owid), window_tabs) in self.windows.items():
            #print(window, file=sys.stderr)
            if key == "ffid":
                returnDict[ffid] = window_tabs
            elif key == "owid":
                returnDict[owid] = {ffid: ffid, tabs: window_tabs}
            else:
                returnDict[ffid + ', ' + owid] = window_tabs
        return returnDict


    def addWindowDict(self, ffid='', windowDict={}):
        owid = ''
        tabs = {}
        if windowDict:
            owid = windowDict.owid
            tabs = windowDict.tabs

        if (not ffid) and (not owid):
            raise Exception('Could not add window dict, no identifiers given')
        if (self.inDict(ffid, owid)):
            raise Exception('Could not add window dict, matching entry loaded')

        self.windows[(ffid, owid)] = tabs


def windowDelta(root_window, reference_window, union_saved):
    return root_window
