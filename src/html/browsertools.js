/**
 * Listen for clicks on the buttons, and send the appropriate message to
 * the content script in the page.
 */
function listenForClicks() {
    document.addEventListener("click", (e) => {

        function onError(error) {
            console.log(`Error: ${error}`);
        }
        function loadFromOrg(reload_scratch) {
            function onLoad(response) {
                //close all in window_array. return list of closed ids
                function cutWindows(window_array) {
                    function onRemoved() {
                        console.log(`Removed window`);
                    }
                    var closedIds = [];
                    for (windowInfo of window_array) {
                        closedIds.push(windowInfo.id);
                        browser.windows.remove(windowInfo.id);
                    }
                    return closedIds;
                }
                //open all in fetched_windows, return list of open ids
                function startWindows(fetched_windows) {
                    function onCreated(windowInfo) {
                        console.log(`Created window: ${windowInfo.id}`);
                        //console.log(window_num);
                        return windowInfo.id;
                    }
                    var openIds = [];
                    var window_num = 1;
                    while (window_num in new_windows){
                        var window_list = new_windows[window_num];
                        var new_window = browser.windows.create(
                            {url: window_list}
                        );
                        new_window.then(onCreated, onError);
                        //newId.then(resolved => {
                        //    console.log(resolved);
                        //}, onError);
                        window_num++;
                    }
                    return openIds;
                }
                var old_windows = browser.windows.getAll();
                var closed_ids = old_windows.then(cutWindows, onError);
                var new_windows = JSON.parse(response);
                var openIds = startWindows(new_windows);
                console.log("Received " + response);
                return response;
            }
            function afterLoad(orgWindows) {
                function saveWindowKeys(foxWindows) {
                    for (windowInfo of foxWindows) {
                        console.log("fox window: " + windowInfo.id);
                    }
                    console.log("org windows: " + orgWindows);
                }
                console.log(`windows loaded`);
                var new_windows = browser.windows.getAll();
                new_windows.then(saveWindowKeys, onError);
            }
            console.log("load data");
            var sending;
            if (reload_scratch) {
                sending = browser.runtime.sendNativeMessage(
                    "fetchorg", JSON.stringify("tru"));
            } else {
                sending = browser.runtime.sendNativeMessage(
                    "fetchorg", JSON.stringify("fals"));
            }
            sending.then(onError, onError);
            //sending.then(onLoad, onError).then(afterLoad, onError);
        }
        function saveWindowData() {
            console.log("save data");
        }
        if (e.target.classList.contains("load-org")) {
            var scratchReload = e.target.nextElementSibling.checked;
            //console.log(scratchReload);
            loadFromOrg(scratchReload);
        } else if (e.target.classList.contains("save-win")) {
            saveWindowData();
        } else if (e.target.classList.contains("save-all")) {
            saveWindowData();
        } else if (e.target.classList.contains("save-reload")) {
            saveWindowData();
        } else if (e.target.classList.contains("clear-local")) {
            console.log("clearing local storage");
            let prom = browser.storage.local.clear();
            prom.then(console.log("cleared"), onError);
        }
    });
}

listenForClicks();
