/**
 * Listen for clicks on the buttons, and send the appropriate message to
 * the content script in the page.
 */
function listenForClicks() {
    document.addEventListener("click", (e) => {

        function onError(error) {
            console.log(`Error: ${error}`);
        }
        function loadFromOrg() {
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
                        return windowInfo.id;
                    }
                    var openIds = [];
                    var window_num = 1;
                    while (window_num in new_windows){
                        var window_list = new_windows[window_num];
                        var new_window = browser.windows.create(
                            {url: window_list}
                        );
                        var newId = new_window.then(onCreated, onError);
                        openIds.push(newId);
                        window_num++;
                    }
                    return openIds;
                }
                var old_windows = browser.windows.getAll();
                var closed_ids = old_windows.then(cutWindows, onError);
                var new_windows = JSON.parse(response);
                var open_ids = startWindows(new_windows);
                console.log("Received " + response);
            }
            function afterLoad() {
                console.log(`windows loaded`);
            }
            console.log("load data");
            var sending = browser.runtime.sendNativeMessage(
                "fetchorg", "Null");
            sending.then(onLoad, onError).then(afterLoad, onError);
        }
        function saveWindowData() {
            console.log("save data");
        }
        if (e.target.classList.contains("load-org")) {
            loadFromOrg();
        } else if (e.target.classList.contains("save-win")) {
            saveWindowData();
        } else if (e.target.classList.contains("save-all")) {
            saveWindowData();
        } else if (e.target.classList.contains("save_reload")) {
            saveWindowData();
        }
    });
}

listenForClicks();
