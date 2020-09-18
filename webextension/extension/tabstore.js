
var DEFAULT_SERVER_NAME = 'http://localhost:5000/';
var DEFAULT_DEVICE_ID = 'default_device';

function onError(error) {
    console.log(`Error: ${error}`);
}

function initListeners(server_name, device_id) {
    function pageChange(requestDetails) {
        function storeWindows(currentWindows) {
            fetch(server_name+'devices/'+device_id, {
                method: 'PUT',
                body: JSON.stringify(currentWindows)
            });
        }

        var getting = browser.windows.getAll({
            populate: true,
            windowTypes: ["normal"]
        });
        getting.then(storeWindows, onError);
    }

    function msgReceiver(message) {
        if (message == 'update-window')
            updateWindows(server_name, device_id);
    }
    
    function tabRemove(tabId, info) {
        if (!info.isWindowClosing) {
            pageChange();
        }
    }

    browser.webRequest.onCompleted.addListener(pageChange, {urls: ["<all_urls>"],
                                                            types: ["main_frame"]});

    browser.windows.onRemoved.addListener(pageChange);

    browser.tabs.onRemoved.addListener(tabRemove);

    browser.tabs.onAttached.addListener(pageChange);

    browser.runtime.onMessage.addListener(msgReceiver);
}

function updateWindows(server_name, dev_id) {
    function readMessage(message) {
        function moveTabs(win_obj, tabs) {
            function moveTab(tab_obj, url, win_id) {
                if (tab_obj.length)
                    browser.tabs.move(tab_obj[0].id, {windowId: win_id, index: -1});
                else
                    browser.tabs.create({url: url, windowId: win_id});
            }
            for (let tab of tabs) {
                browser.tabs.query({
                    windowId: tab.id, url: tab.url
                }).then(result => moveTab(result, tab.url, win_obj.id)).catch(onError);
            }
        }
        function openWindow(tabs) {
            var moved_tabs = [];
            var open_urls = [];
            for (let tab of tabs) {
                if (tab.id)
                    moved_tabs.push(tab);
                else
                    open_urls.push(tab.url);
            }
            browser.windows.create({
                url: open_urls
            }).then(result => moveTabs(result, moved_tabs)).catch(onError);
        }

        function updateWindows(stored_windows) {
            var new_windows = [];
            if (message.p_open)
                for (var i = 0; i < message.p_open.length; i++) {
                    var tabs = message.p_open[i].tabs;
                    openWindow(tabs);
                }
            if (message.change) {}
            if (message.close) {}
        }
        browser.windows.getAll({windowTypes: ["normal"]})
            .then(updateWindows).catch(onError);
    }
    fetch(server_name + 'devices/' + dev_id + '/messages', {method: 'GET'})
        .then(response => response.json()).then(message =>
                                                readMessage(JSON.parse(message)));
}

browser.storage.local.get(['server_name', 'device_id']).then(result => {
    var server_name = result.server_name;
    var device_id = result.device_id;
    if (server_name && device_id) {
        initListeners(server_name, device_id);
    } else {
        if (!server_name)
            server_name = DEFAULT_SERVER_NAME;
        if (!device_id)
            device_id = DEFAULT_DEVICE_ID;

        browser.storage.local.set({'server_name': server_name, 'device_id': device_id})
            .then(initListeners(server_name, device_id),onError);
    }
}).catch(onError);
