/**
 * Listen for clicks on the buttons, and send the appropriate message to
 * the content script in the page.
 */
function listenForClicks() {
    document.addEventListener("click", (e) => {

        function onError(error) {
            console.log(`Error: ${error}`);
        }
        function onSuccess(response) {
            console.log(`success: ${response}`);
            return null;
        }
        function debugObj(obj) {
            console.log('Passed Object as string:');
            console.log(JSON.parse(obj));
        }
        function loadFromOrg(reload_scratch) {
            function onOrgLoad(response) {
                function changeWindows(storage_message) {
                    function changeWindow(ffid, owid) {
                        var tabDelta = Object.assign({}, delta[owid]['tabs']);
                        //execute action for each tab
                    }
                    function onSuccess(response) {
                        //console.log("storage_message");
                        //console.log(storage_message);
                        console.log(`success: ${response}`);
                        return null;
                    }
                    function addWindow(owid) {
                        //console.log(`+promise to add ${owid} to browser`);
                        var tabList = Object.keys(delta[owid]['tabs']);
                        let add_promise = browser.windows.create({url: tabList});
                        //let storage_promise = add_promise.then(storageAdd, onError);
                        return add_promise;
                    }
                    function newWindowId(win_msg){
                        //console.log(`+new window ${win_msg.id}`);
                        return win_msg.id;
                    }
                    function storageAdd(ffid) {
                        //console.log(`+promise add ${ffid}, ${this.owid} to storage`);
                        //console.log(
                        //    `+adding ${this.owid} to storage w/ ffid ${ffid}`);
                        load_obj[ffid] = {
                            owid: this.owid,
                            tabs: delta[this.owid]['tabs']
                        };
                        let load_msg = load_obj;
                        let save_promise = browser.storage.local.set({load_msg});
                        return save_promise;
                    }
                    function cutWindow(ffid) {
                        console.log(`+removing ${ffid}`);
                        let cut_promise = browser.windows.remove(parseInt(ffid));
                        return cut_promise;
                    }
                    var storage_windows = storage_message['windows'];
                    var load_obj = {};
                    let next_action = null;
                    for (let [ owid, window ] of Object.entries(delta)) {
                        console.log(`+checking ${owid} for any actions`);
                        if ('action' in window) {
                            console.log(`+${window['action']} this window`);
                            if (window['action'] == 'remove') {
                                //delete storage_windows[parseInt(window['ffid'])];
                                next_action = cutWindow(window['ffid']);
                                next_action = next_action.then(onSuccess, onError);
                            }
                            else if (window['action'] == 'add') {
                                next_action = addWindow(owid);
                                console.log("+addWindow");
                                let new_ffid = next_action.then(newWindowId, onError);
                                console.log("+storageAdd");
                                next_action = new_ffid.then(storageAdd.bind({owid: owid}));
                                console.log("+resolve");
                                //console.log('next_action');
                                //console.log(next_action);
                                next_action = next_action.then(onSuccess, onError);
                            }
                        }
                        else {
                            console.log(`+checking ${owid} tabs for any actions`);
                            if (window['ffid'] in storage_windows) {
                                next_action = changeWindow(window['ffid'], owid);
                            }
                        }
                    }
                    //console.log('storage_windows');
                    //console.log(storage_windows);
                    return storage_windows;
                }
                function getStorageWindow() {
                    let store_promise = browser.storage.local.get("windows");
                    return store_promise;
                }
                var delta = JSON.parse(response);
                console.log('delta');
                console.log(delta);
                let storage = getStorageWindow();
                let update = storage.then(changeWindows);
                console.log('update');
                //update.then(onSuccess,onError);
                //console.log(update);
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
                    "fetchorg", JSON.stringify(true));
            } else {
                sending = browser.runtime.sendNativeMessage(
                    "fetchorg", JSON.stringify(false));
            }
            var loaded = sending.then(onOrgLoad, onError);
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
        }
        else if (e.target.classList.contains("clear-local")) {
            console.log("clearing local storage");
            let prom = browser.storage.local.clear();
            prom.then(console.log("cleared"), onError);
        }
        else if (e.target.classList.contains("print-local")) {
            console.log("smorgasbord local storage:");
            let prom = browser.storage.local.get();
            prom.then(response => {console.log(response);}, onError);
        }
    });
}

listenForClicks();
