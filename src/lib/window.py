import sys

class Windows:
    def __init__(self, windowDict={}):
        self.windows = {}
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
        

    def matchID(self, ffid='', owid=''):
        match = {}
        if not ffid:
            for (o_ffid, o_owid) in self.windows:
                if owid == o_owid:
                    match['ffid'] = o_ffid
                    match['tabs'] = self.windows[(o_ffid, o_owid)]
                    break
        elif not owid:
            for (o_ffid, o_owid) in self.windows:
                if ffid == o_ffid:
                    match['owid'] = o_owid
                    match['tabs'] = self.windows[(o_ffid, o_owid)]
                    break
        elif (ffid, owid) in self.windows:
            match['tabs'] = self.windows[(o_ffid, o_owid)]
        return match

    def tabKey(self, keypair, ffid='', owid=''):
        for (o_ffid, o_owid), tabs in self.windows.items():
            if ((not ffid) or ffid == o_ffid) and ((not owid) or owid == o_owid):
                tabs.update(keypair)
                #for tab in tabs.values():
                #    tab.update(keypair)

    def asDict(self, key=None):
        returnDict = {}
        for ((ffid, owid), window_tabs) in self.windows.items():
            action = None
            if 'action' in window_tabs:
                action = window_tabs['action']
                del window_tabs['action']
            if key == "ffid":
                returnDict[ffid] = {'owid': owid, 'tabs': window_tabs}
                win_key = ffid
            elif key == "owid":
                returnDict[owid] = {'ffid': ffid, 'tabs': window_tabs}
                win_key = owid
            else:
                win_key = ffid + ', ' + owid
                returnDict[win_key] = window_tabs
            if action:
                returnDict[win_key]['action'] = action
        return returnDict


    def addWindowDict(self, ffid='', owid='', tabDict={}):
        if (not ffid) and (not owid):
            raise Exception('Could not add window dict, no identifiers given')
        if (self.inDict(ffid, owid)):
            raise Exception('Could not add window dict, matching entry loaded')
        self.windows[(ffid, owid)] = tabDict

#def matchTabs(tab, o_tab):
#    for key in tab:
#        if key in o_tab:
#            if tab[key] != o_tab[key]:
#                return false
        #print(tabs, file=sys.stderr)
#def mergeTabs(tab, o_tab, pref=None):
#    if pref == None:
#        pass

def initFromOrg(windowDict):
    orgWindows = Windows()
    for owid, tabs in windowDict.items():
        orgWindows.addWindowDict(owid=owid, tabDict=tabs)
    return orgWindows

def windowDelta(root_window, reference_window, intersect):
    delta = Windows()
    for (ffid, owid), tabs in reference_window.windows.items():
        if root_window.inDict(owid=owid):
            root_match = root_window.matchID(owid=owid)
            tab_delta = {}
            for tab, tab_data in tabs.items():
                if tab not in root_match['tabs']:
                    tab_delta[tab] = tab_data
                    tab_delta[tab]['action'] = 'add'
                else:
                    tab_delta[tab] = tab_data
                    tab_delta[tab]['action'] = 'update'
            for tab, tab_data in root_match['tabs']:
                if tab not in tab_delta:
                    if intersect or (tab_data['stored'] is True):
                        tab_delta[tab] = tab_data
                        tab_delta[tab]['action'] = 'remove'
            delta.addWindowDict(root_match['ffid'], owid, tab_delta)
        else:
            delta.addWindowDict(owid=owid, tabDict=tabs)
            delta.tabKey({'action': 'add'}, owid=owid)

    #check for windows not found in reference_window
    for (ffid, owid), tabs in root_window.windows.items():
        if reference_window.inDict(ffid, owid):
            continue
        elif (intersect
              or all(tabData['stored'] is True for tabData in tabs.values())):
            delta.addWindowDict(ffid, owid, tabDict={'action':'remove'})
        elif (all(tabData['stored'] is False for tabData in tabs.values())):
            continue
        else:
            tab_delta = {}
            for tab, tabData in tabs.items():
                tab_delta[tab] = tabData
                if tabData['stored'] is True:
                    tab_delta[tab]['action'] = 'remove'
            delta.addWindowDict(ffid, owid, tab_delta)

    return delta
