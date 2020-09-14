

function onError(error) {
    var err_blk = document.createElement('div');
    err_blk.className = 'error';
    err_blk.innerHTML = error;
    document.getElementById('content-field').appendChild(err_blk);
}

function tabFind(tab_arr) {
    var request_url = new URL(SERVER_NAME+'link');
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
}

function saveLink(link_id, link_url, link_title) {
    document.getElementById('link-title').setAttribute('value', link_title);
    document.getElementById('link-url').innerHTML = link_url;
    document.getElementById('link-id').innerHTML = link_id;
    fetch(SERVER_NAME+'tags/list', {method: 'GET'}).then(response => response.json())
        .then(result => {
            autocomplete(document.getElementById('tag-add'), result.tags);
        }).catch(onError);
    document.getElementById('btn-tag-add').addEventListener('click', function(e) {
        var tag = document.getElementById('tag-add').value;
        var title = document.getElementById('link-title').value;
        fetch(SERVER_NAME+'link', {method: 'POST',
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
    fetch(SERVER_NAME+'link/'+link_id,
          {method: 'GET'}).then(response => response.json())
        .then(link_data => {
            var request_url = new URL(SERVER_NAME+'link/tags');
            request_url.searchParams.append('link_id', link_id);
            fetch(request_url, {method: 'GET'}).then(response => response.json())
                .then(tag_data => {
                    document.getElementById('link-summary').appendChild(
                        linkSummary(link_data, tag_data.result));
                }).catch(onError);
        }).catch(onError);
}

function editServer(server_url) {
    showMenu('server-name');
    document.getElementById('old-server-url').innerHTML = server_url;
    document.getElementById('new-server-url').value = server_url;
}

function newTag() {
    showMenu('new-tag');
    fetch(SERVER_NAME+'tags/list', {method: 'GET'}).then(response => response.json())
        .then(result => {
            autocomplete(document.getElementById('parent-add'), result.tags);
        }).catch(onError);
    document.getElementById('btn-tag-new').addEventListener('click', function(e) {
        var new_id = document.getElementById('inp-tag-new').value;
        var parent_id = document.getElementById('parent-add').value;
        var tag_desc = document.getElementById('inp-tag-desc-add').value;
        fetch(SERVER_NAME+'tag/'+new_id, {
            method: 'PUT',
            body: JSON.stringify({parent: parent_id, desc: tag_desc})
        }).then(response => response.json()).then(result => {}).catch(onError);
    });
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

var SERVER_NAME = 'http://127.0.0.1:5000/';

document.getElementById('server-name-start').addEventListener("click", function(e) {
    editServer(SERVER_NAME);
});

document.getElementById('new-tag-start').addEventListener("click", function(e) {
    newTag(SERVER_NAME);
});

let tab_query = browser.tabs.query({currentWindow: true, active: true});
tab_query.then(tabFind, onError);
