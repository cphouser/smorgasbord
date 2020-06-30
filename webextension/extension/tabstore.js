
var device_id = 'default_device';

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
    console.log(currentWindows);
    fetch('http://127.0.0.1:5000/devices/'+device_id, {
    method: 'PUT',
    body: JSON.stringify(currentWindows),
    })
    .then(response => response.json())
    .then(result => {
      console.log('Success:', result);
    })
    .catch(error => {
      console.error('Error:', error);
    });
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
