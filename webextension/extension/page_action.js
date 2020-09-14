

function autocomplete(inp, arr) {
    var current_focus;
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        closeAllLists();
        if (!val) {return false;}
        current_focus = -1;
        //container for autocomplete list
        a = document.createElement("div");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(a);
        //add each matching entry from array
        for (i = 0; i < arr.length; i++) {
            if (arr[i].id.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                b = document.createElement("div");
                if (arr[i].pre.length) {
                    addAncestorLines(b, i, arr[i].pre.length);
                }
                b.innerHTML += "<strong>" +
                    arr[i].id.substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].id.substr(val.length);
                b.innerHTML += "<input type='hidden' value='" + arr[i].id + "'>";
                b.addEventListener("click", function(e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });

    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            //down arrow
            current_focus++;
            addActive(x);
        } else if (e.keyCode == 38) {
            //up arrow
            current_focus--;
            addActive(x);
        } else if (e.keyCode == 13) {
            //enter key
            e.preventDefault();
            if (current_focus > -1) {
                if (x) x[current_focus].click();
            }
        }
    });

    function addAncestorLines(elem, idx, depth) {
        //elem.innerHTML += '<span style="color:#aaaaaa">';
        var ancestor_container = document.createElement('span');
        ancestor_container.setAttribute('class', 'ancestor');
        var ancestors = "";
        while (depth > 1) {
            while (arr[idx].pre.length >= depth) idx--;
            ancestors = arr[idx].id + '\u2b95' + ancestors;
            depth--;
        }
        ancestor_container.innerHTML = ancestors;
        elem.appendChild(ancestor_container);
    }

    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (current_focus >= x.length) current_focus = 0;
        if (current_focus < 0) current_focus = (x.length - 1);

        x[current_focus].classList.add("autocomplete-active");
        x[current_focus].scrollIntoView();
    }

    function removeActive(x) {
        //remove "active" class from all autocomplete items
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(element) {
        //close all autocomplete lists except the one passed as an argument
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (element != x[i] && element != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
}

function showMenu(menu_id) {
    var hidden_menus = document.getElementsByClassName('hidden-menu');
    for (var i = 0; i < hidden_menus.length; i++)
        hidden_menus[i].style.display = 'none';
    document.getElementById(menu_id).style.display = 'block';
    var menu_buttons = document.getElementsByClassName('menu-button');
    for (var i = 0; i < menu_buttons.length; i++) {
        if (menu_buttons[i].id == menu_id + '-start')
            menu_buttons[i].disabled = true;
        else
            menu_buttons[i].disabled = false;
    }
}

function disableMenu(buttons) {
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
    }
}

function editServer(server_url, device_id) {
    showMenu('server-name');
    document.getElementById('old-server-url'
                           ).innerHTML = 'current server url: ' + server_url;
    document.getElementById('new-server-url').value = server_url;
    document.getElementById('old-device-id'
                           ).innerHTML = 'current device id: ' + device_id;
    document.getElementById('new-device-id').value = device_id;
    document.getElementById('save-server').addEventListener('click', function(e) {
        var new_name = document.getElementById('new-server-url').value;
        var new_dev_id = document.getElementById('new-device-id').value;
        if (!new_name) new_name = server_url;
        if (!new_dev_id) new_dev_id = device_id;
        browser.storage.local.set({'server_name': new_name, 'device_id': new_dev_id})
            .then(window.close()).catch(initError);

    });
    document.getElementById('ping-server').addEventListener('click', function(e) {
        var new_name = document.getElementById('new-server-url').value;
        if (new_name) {
            checkServer(new_name, document.getElementById('server-ping-result'));
        }
    });
}

function checkServer(server_name, return_elem) {
    var found = fetch(server_name + 'smorgasbord', {method: 'GET'}).then(
        response => response.json()).then(result => {
                if (return_elem) return_elem.innerHTML = JSON.stringify(result);
                return (result.status == 'online');
            }).catch(error => {
                if (return_elem) return_elem.innerHTML = error;
                return false;
            });
    return found;
}

function linkSummary(link_data, tag_data) {
    var summary_div = document.createElement('div');
    if (link_data.parent) {
        var ancestor_container = document.createElement('span');
        ancestor_container.setAttribute('class', 'ancestor');
        ancestor_container.innerHTML = link_data.parent + '\u2b95';
        summary_div.appendChild(ancestor_container);
    }
    if (link_data.title) {
        var link_title = document.createElement('h3');
        link_title.innerHTML = link_data.title;
        summary_div.appendChild(link_title);
    }
    var link_url = document.createElement('em');
    link_url.innerHTML = link_data.url;
    summary_div.appendChild(link_url);
    var tag_list = document.createElement('p');
    for (var tag_id in tag_data) {
        var tag = document.createElement('a');
        tag.innerHTML = tag_id;
        tag_list.appendChild(tag);
    }
    summary_div.appendChild(tag_list);
    var link_desc = document.createElement('p');
    if (link_data.desc) link_desc.innerHTML = link_data.desc;
    else link_desc.innerHTML = '[no description]';
    summary_div.appendChild(link_desc);
    return summary_div;
}

function initPage(server_name, device_id) {
    function saveLink(link_id, link_url, link_title) {
        document.getElementById('link-title').setAttribute('value', link_title);
        document.getElementById('link-url').innerHTML = link_url;
        document.getElementById('link-id').innerHTML = link_id;
        fetch(server_name+'tags/list', {method: 'GET'}).then(response => response.json())
            .then(result => {
                autocomplete(document.getElementById('tag-add'), result.tags);
            }).catch(onError);
        document.getElementById('btn-tag-add').addEventListener('click', function(e) {
            var tag = document.getElementById('tag-add').value;
            var title = document.getElementById('link-title').value;
            fetch(server_name+'link', {method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({
                                        url: link_url,
                                        title: title,
                                        tag: tag,
                                    })}).then(response => response.json())
                .then(onError).catch(onError);
        });
        //get related links for link relation selector
    }

    function editLink(link_id) {
        fetch(server_name+'link/'+link_id,
              {method: 'GET'}).then(response => response.json())
            .then(link_data => {
                var request_url = new URL(server_name+'link/tags');
                request_url.searchParams.append('link_id', link_id);
                fetch(request_url, {method: 'GET'}).then(response => response.json())
                    .then(tag_data => {
                        document.getElementById('link-summary').appendChild(
                            linkSummary(link_data, tag_data.result));
                    }).catch(onError);
            }).catch(onError);
    }

    function tabFind(tab_arr) {
        var request_url = new URL(server_name+'link');
        request_url.searchParams.append('url', encodeURI(tab_arr[0].url));
        fetch(request_url, {
            method: 'GET',
        }).then(response => response.json())
            .then(result => {
                document.getElementById('link-id').innerHTML = result.link_id;
                switch(result.status) {
                case 'unsaved':
                    showMenu('unsaved-link');
                    saveLink(result.link_id, tab_arr[0].url, tab_arr[0].title);
                    break;
                case 'saved':
                    showMenu('saved-link');
                    editLink(result.link_id);
                    break;
                }
            }).catch(onError);
    }

    function newTag() {
        showMenu('new-tag');
        fetch(server_name+'tags/list', {method: 'GET'}).then(response => response.json())
            .then(result => {
                autocomplete(document.getElementById('parent-add'), result.tags);
            }).catch(onError);
        document.getElementById('btn-tag-new').addEventListener('click', function(e) {
            var new_id = document.getElementById('inp-tag-new').value;
            var parent_id = document.getElementById('parent-add').value;
            var tag_desc = document.getElementById('inp-tag-desc-add').value;
            fetch(server_name+'tag/'+new_id, {
                method: 'PUT',
                body: JSON.stringify({parent: parent_id, desc: tag_desc})
            }).then(response => response.json()).then(result => {}).catch(onError);
        });
    }

    checkServer(server_name, document.getElementById('server-ping-result')).then(
        result => {
            if (!result)
                throw "couldn't connect to server";

            document.getElementById('server-name-start')
                .addEventListener("click", e => editServer(server_name, device_id));

            document.getElementById('new-tag-start').
                addEventListener("click", newTag);

            let tab_query = browser.tabs.query({currentWindow: true, active: true});
            tab_query.then(tabFind, onError);
        }).catch(
            error => {
                editServer(server_name, device_id);
                initError(error);
            });
}

function onError(error) {
    var err_blk = document.createElement('div');
    err_blk.className = 'error';
    err_blk.innerHTML = error;
    document.getElementById('content-field').appendChild(err_blk);
}

function initError(error) {
    disableMenu(document.getElementsByClassName('menu-button'));
    showMenu('server-name');
    if (error) onError(error);
}

browser.storage.local.get(['server_name', 'device_id']).then(result => {
    var server_name = result.server_name;
    var device_id = result.device_id;
    if (server_name && device_id) {
        initPage(server_name, device_id);
    } else initError('invalid server settings: '
                     + JSON.stringify({'server_name': server_name,
                                       'device_id': device_id}));
}).catch(initError);
