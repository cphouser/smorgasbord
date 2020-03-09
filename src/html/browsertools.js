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
                        let tabDelta = Object.assign({}, delta[owid]['tabs']);
                        let addTabs = [];
                        let updateTabs = {};
                        let removeTabs = [];
                        //console.log(`+${ffid}: ${owid} tabs`);
                        for (let [tab, tabData] of Object.entries(tabDelta)) {
                            let tab_action = tabData.action;
                            delete tabData.action;
                            //console.log(tab);
                            if (tab_action == 'remove') {
                                removeTabs.push(tab);
                            }
                            else if (tab_action == 'update') {
                                updateTabs[tab] = tabData;
                            }
                            else if (tab_action == 'add') {
                                addTabs.push(tab);
                                updateTabs[tab] = tabData;
                            }
                            else {
                                console.log(`unknown tab action: ${tab_action}`);
                            }
                        }
                        //console.log("updateTabs");
                        //console.log(updateTabs);
                        //console.log("removeTabs");
                        //console.log(removeTabs);
                        //console.log("addTabs");
                        //console.log(addTabs);
                        return [updateTabs, removeTabs, addTabs];
                    }
                    function onSuccess(response) {
                        console.log(`success: ${response}`);
                        return null;
                    }
                    function addWindow(owid) {
                        //console.log(`+promise to add ${owid} to browser`);
                        var tabList = Object.keys(delta[owid]['tabs']);
                        let add_promise = browser.windows.create({url: tabList});
                        return add_promise;
                    }
                    function newWindowId(win_msg){
                        //console.log(`+new window ${win_msg.id}`);
                        return win_msg.id;
                    }
                    function storageAddWindow(ffid) {
                        //console.log(`+promise add ${ffid}, ${this.owid} to storage`);
                        //console.log(
                        //    `+adding ${this.owid} to storage w/ ffid ${ffid}`);
                        load_obj[ffid] = {
                            owid: this.owid,
                            tabs: delta[this.owid]['tabs']
                        };
                        //console.log("load_obj");
                        //console.log(load_obj);
                        let load_msg = load_obj;
                        let store_promise = browser.storage.local.set({load_msg});
                        return store_promise;
                    }
                    function storeWindow(ffid, owid, tabsObj) {
                        load_obj[ffid] = {
                            owid: owid,
                            tabs: tabsObj
                        };
                        //console.log("load_obj");
                        //console.log(load_obj);
                        let load_msg = load_obj;
                        let save_promise = browser.storage.local.set({load_msg});
                        return save_promise;
                    }
                    function addTabs(response) {
                        for (const tab_url of this.tabs) {
                            browser.tabs.create({
                                url: tab_url,
                                windowId: parseInt(this.ffid)
                            });
                        }
                    }
                    function removeTabs(ffid, tabList) {
                        function removeById(tabArray) {
                            let id_list = [];
                            for (const tab of tabArray) {
                                if (tabList.includes(tab.url)
                                        && (tab.id != (browser.tabs.TAB_ID_NONE))) {
                                    id_list.push(tab.id);
                                }
                            }
                            //console.log(id_list);
                            return browser.tabs.remove(id_list);

                        }
                        let tabs_promise = browser.tabs.query(
                                {windowId: parseInt(ffid)});
                        let remove_promise = tabs_promise.then(removeById, onError);
                        return remove_promise;
                    }
                    function cutWindow(ffid) {
                        //console.log(`+removing ${ffid}`);
                        let cut_promise = browser.windows.remove(parseInt(ffid));
                        return cut_promise;
                    }
                    var storage_windows = storage_message['windows'];
                    var load_obj = {};
                    let next_action = null;
                    for (let [ owid, window ] of Object.entries(delta)) {
                        //console.log(`+checking ${owid} for any actions`);
                        if ('action' in window) {
                            //console.log(`+${window['action']} this window`);
                            if (window['action'] == 'remove') {
                                next_action = cutWindow(window['ffid']);
                                next_action = next_action.then(onSuccess, onError);
                            }
                            else if (window['action'] == 'add') {
                                next_action = addWindow(owid);
                                let new_ffid = next_action.then(newWindowId, onError);
                                next_action = new_ffid.then(storageAddWindow.bind({owid: owid}));
                                next_action = next_action.then(onSuccess, onError);
                            }
                        }
                        else {
                            //console.log(`+checking ${owid} tabs for any actions`);
                            if (window['ffid'] in storage_windows) {
                                const [updates, removes, adds] =
                                            changeWindow(window['ffid'], owid);
                                next_action = removeTabs(window['ffid'], removes);
                                next_action = next_action.then(onSuccess, onError);
                                let save_promise = storeWindow(
                                    window['ffid'], owid, updates);
                                save_promise.then(addTabs.bind(
                                    {ffid: window['ffid'], tabs: adds}));
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
                //console.log('delta');
                //console.log(delta);
                let storage = getStorageWindow();
                let update = storage.then(changeWindows);
                //console.log('update');
                //update.then(onSuccess,onError);
                //console.log(update);
                return response;
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
        }
        function saveWindowData() {
            console.log("save data");
        }
        if (e.target.classList.contains("load-org")) {
            var scratchReload = e.target.nextElementSibling.checked;
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
