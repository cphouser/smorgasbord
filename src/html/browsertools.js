/**
 * Listen for clicks on the buttons, and send the appropriate message to
 * the content script in the page.
 */
function listenForClicks() {
    document.addEventListener("click", (e) => {
        function onResponse(response) {
            function onCreated(windowInfo) {
                console.log(`Created window: ${windowInfo.id}`);
            }
            function idList(window_array) {
                function onRemoved() {
                    console.log(`Removed window`);
                }
                var id_array = [];
                for (windowInfo of window_array) {
                    id_array.push(windowInfo.id);
                    browser.windows.remove(windowInfo.id);
                }
                return id_array;
            }
            var old_windows = browser.windows.getAll();
            old_windows.then(idList, onError);
            var new_windows = JSON.parse(response);
            var window_num = 1;
            while (window_num in new_windows){
                var window_list = new_windows[window_num];
                var new_window = browser.windows.create({url: window_list});
                new_window.then(onCreated, onError);
                window_num++;
            }
            console.log("Received " + response);
        }

        function onError(error) {
            console.log(`Error: ${error}`);
        }

        function loadWindowData() {
            console.log("load data");
            var sending = browser.runtime.sendNativeMessage(
                "fetchorg", "Null");
            sending.then(onResponse, onError);
            //run org fetcher
            //get window data from org fetcher
            //load tabs and windows
        }

        function saveWindowData() {
            console.log("save data");
        }

        if (e.target.classList.contains("load")) {
            loadWindowData();
        }
        else if (e.target.classList.contains("save")) {
            saveWindowData();
        }
    });
}

listenForClicks();
