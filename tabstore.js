
function pageChange(requestDetails) {
    let querying = browser.tabs.query({});
    querying.then(storeTabs, onError);
}

function onError(error) {
    console.log(`Error: ${error}`);
}

function storeTabs(tabs) {
    var win_obj = {};
    for (let tab of tabs) {
        if (!(tab.windowId in win_obj)) {
            win_obj[tab.windowId] = [];
        } 
        win_obj[tab.windowId].push({
            url: tab.url,
            title: tab.title
        });
        //console.log(tab.url);
        //console.log(tab.windowId);
        //console.log(tab.title);
    }
    var varb = browser.runtime.sendNativeMessage("tabstore", JSON.stringify(win_obj));
}

function tabRemove(tabId, info) {
    if (!info.isWindowClosing) {
        pageChange();
    }
};

browser.webRequest.onCompleted.addListener(
    pageChange,
    {urls: ["<all_urls>"],
     types: ["main_frame"]}
);

browser.windows.onRemoved.addListener(pageChange);

//passes tabId and removeInfo (windowId, isWindowClosing)
browser.tabs.onRemoved.addListener(tabRemove);

browser.tabs.onAttached.addListener(pageChange);
