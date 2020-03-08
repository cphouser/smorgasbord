
function pageChange(requestDetails) {
    console.log("page change");
    var getting = browser.windows.getAll({
        populate: true,
        windowTypes: ["normal"]
    });
    getting.then(storeWindows, onError);
}

function onError(error) {
    console.log(`Error: ${error}`);
}

function storeWindows(currentWindows) {
    function resaveTabs(storageObject) {
        var storedWindows = storageObject.windows;
        //console.log("storedWindows");
        //console.log(storedWindows);
        var lostTabs = {};
        console.log("iterating over each current window");
        for (let windowInfo of currentWindows) {
            lostTabs[windowInfo.id] = [];
            var currentTabs = windowInfo.tabs;
            if ((typeof(storedWindows) === "object")
                && (windowInfo.id in storedWindows)) {
                console.log(`+window ${windowInfo.id} is in storage by ID`);
                win_obj[windowInfo.id] = {
                    owid: storedWindows[windowInfo.id].owid,
                    tabs: {}
                };
                for (let tab of currentTabs) {
                    if (tab.url in storedWindows[windowInfo.id].tabs) {
                        //console.log(`++tab ${tab.url} in matching storage`);
                        win_obj[windowInfo.id].tabs[tab.url] =
                            storedWindows[windowInfo.id].tabs[tab.url];
                    } else {
                        //console.log(`++tab ${tab.url} not in matching storage`);
                        lostTabs[windowInfo.id].push({
                            url: tab.url,
                            title: tab.title
                        });
                    }
                } 
            }
            else if (typeof(storedWindows) === "object") {
                console.log(`+window ${windowInfo.id} not in storage by FFID`);
                console.log("+checking stored windows for other matches");
                for (const [ storedWindowId, storedWindow ]
                     of Object.entries(storedWindows)) {
                    var found = false;
                    if (Object.keys(storedWindow.tabs).every(st_url => {
                            currentTabs.some(ct => ct.url == st_url);
                        })) {
                        console.log(`++window ${storedWindowId} is a match`);
                        win_obj[windowInfo.id] = storedWindow;
                        console.log(`++adding unmatched tabs to lostTabs`);
                        for (let tab of currentTabs) {
                            if (!(tab.url in storedWindow.tabs)) {
                                lostTabs[windowInfo.id].push({
                                    url: tab.url,
                                    title: tab.title
                                });
                            }
                        }
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    console.log(`+FF Window ${windowInfo.id} not in storage`);
                    console.log(`+Adding all tabs to lost tabs`);
                    for (let tab of currentTabs) {
                        lostTabs[windowInfo.id].push({
                            url: tab.url,
                            title: tab.title
                        });
                    }
                }
            }
            else {
                console.log("+no windows in storage");
                console.log(`+Adding all tabs to lost tabs`);
                for (let tab of currentTabs) {
                    lostTabs[windowInfo.id].push({
                        url: tab.url,
                        title: tab.title
                    });
                }
            }
        }
        console.log("iterating over each window's lost tabs");
        for (let [ lostWindowId, lostWindowTabs ] of Object.entries(lostTabs)) {
                var foundTabs = [];
                var windowData = {};
            //console.log("+lostWindowTabs");
            //console.log(lostWindowTabs);
            if (Object.keys(lostWindowTabs).length == 0) {
                continue;
            }
            if ((typeof(storedWindows) === "object")) {
                //console.log("+checking storage for each of the lost tabs");
                for (let [idx, tab] of lostWindowTabs.entries()) {
                    let storedWindowIds = Object.keys(storedWindows);
                    if (storedWindowIds.some(storedWindow => {
                            var storedWindowObj = storedWindows[storedWindow];
                            if (tab.url in storedWindowObj.tabs) {
                                foundTabs.push({
                                    url: tab.url,
                                    ffid: storedWindow,
                                    owid: storedWindowObj.owid,
                                    storedata: storedWindowObj.tabs[tab.url]
                                });
                                return true;
                            } else {
                                return false;
                            }})) {
                        lostWindowTabs.splice(idx, 1);
                    }
                }
            }
            //else {
            //    console.log("+storage unitialized or no lost tabs");
            //}
            if (foundTabs.length) {
                if (foundTabs.every((foundTab, tabIdx, tabArray) => {
                        return (foundTab.ffid == tabArray[0].ffid);
                        })) {
                    //console.log("+assign lost tabs OWID from storage to windowData");
                    windowData.owid = foundTabs[0].owid;
                }
                let windowTabs = {};
                //console.log("+adding found tabs to windowData");
                for (let tab of foundTabs) {
                    windowTabs[tab.url] = tab.storedata;
                }
                //console.log("+windowTabs");
                //console.log(windowTabs);
                windowData.tabs = windowTabs;
            }
            else {
                //console.log("+no tabs found in storage, init empty windowData.tabs");
                windowData.tabs = {};
            }
            //console.log("+adding still lost tabs to windowData.tabs");
            for (const tab of lostWindowTabs) {
                windowData.tabs[tab.url] = {
                    title: tab.title,
                    stored: false
                };
            }
            //console.log("+checking win_obj for the lost window FFID");
            if (lostWindowId in win_obj) {
                //console.log("+win_obj[lostWindowId]");
                //console.log(win_obj[lostWindowId]);

                //console.log("+add lost tabs to the found win_obj");
                for (const [tab, tabData] of Object.entries(windowData.tabs)) {
                    if (!(tab in win_obj[lostWindowId].tabs)) {
                        //console.log(`++adding tab ${tab} to ${lostWindowId}`);
                        win_obj[lostWindowId].tabs[tab] = tabData;
                    }
                }
            }
            else if (!("owid" in windowData) || windowData.owid === undefined) {
                //console.log("+lost window not in win_obj. generating its OWID.");
                let i = 0;
                let newOWID = "browser_" + i.toString();
                let owidList = Object.values(win_obj).map((windowEntry) => windowEntry.owid);
                console.log(owidList);
                while (owidList.includes(newOWID)) {
                    i++;
                    newOWID = "browser_" + i.toString();
                }
                //console.log(newOWID);
                windowData.owid = newOWID;
                win_obj[lostWindowId] = windowData;
            }
            else {
                //console.log("+lost window not in win_obj but already has an OWID");
                win_obj[lostWindowId] = windowData;
            }
        }
        let windows = win_obj;
        var savePromise = browser.storage.local.set({windows});
        return savePromise;
    }
    function sendWindowMessage() {
        var sending = browser.runtime.sendNativeMessage(
            "tabstore", JSON.stringify(win_obj)
        );
        sending.then(onError, onError);
    }
    var win_obj = {};
    var loadResults = browser.storage.local.get("windows");
    var saveResults = loadResults.then(resaveTabs, onError);
    saveResults.then(sendWindowMessage, onError);
}

function tabRemove(tabId, info) {
    if (!info.isWindowClosing) {
        pageChange();
    }
};

browser.webRequest.onCompleted.addListener(
    pageChange,
    {urls: ["<all_urls>"], types: ["main_frame"]}
);

browser.windows.onRemoved.addListener(pageChange);

browser.tabs.onRemoved.addListener(tabRemove);

browser.tabs.onAttached.addListener(pageChange);
