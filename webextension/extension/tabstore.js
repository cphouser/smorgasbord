
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
            })
                .then(response => response.json())
                .then(result => {
                    console.log('Success:', result);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        var getting = browser.windows.getAll({
            populate: true,
            windowTypes: ["normal"]
        });
        getting.then(storeWindows, onError);
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
            .then(initListeners(server_name, device_id)).catch(onError);
    }
    onError(JSON.stringify(result));
}).catch(onError);
