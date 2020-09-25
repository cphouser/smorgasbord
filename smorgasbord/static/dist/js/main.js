

$.deselect = function(data_link_id) {
    $.each($("input[name='link']:checked"), function() {
        if (!data_link_id || $(this).attr('data-link-id') == data_link_id)
            $(this).prop('checked', false);
    });
};

$.selected = function(data_link_id) {
    var selected = [];
    $.each($("input[name='link']:checked"), function() {
        if (!data_link_id || $(this).attr('data-link-id') == data_link_id)
            selected.push($(this).val());
    });
    return selected;
};

$.togg_link_table = function(tag_id) {
    var display_div = $('div#'+tag_id+'-link-table');
    var tools_div = $('div#'+tag_id+'-msg-tools');
    if (display_div.attr('style') == 'display:none;') {
        display_div.attr('style', 'display:block;');
        tools_div.attr('style', 'display:block;');
        return true;
    } else {
        display_div.attr('style', 'display:none;');
        tools_div.attr('style', 'display:none;');
        return false;
    }
};

$.load_links = function(tag_id, order) {
    var ret_div = $('div#'+tag_id+'-link-table');
    if (!order) order = 'alpha';
    $.getJSON('/tag/'+tag_id+'/links', {
        order: order
    }, function(data) {
        var table = $('<table></table>');
        table.attr('class', 'link-table');
        $.each(data.result, function (_, link) {
            var row = $('<tr></tr>');
            var select = $('<input type="checkbox", name="link">');
            select.attr('value', link.id);
            select.attr('data-link-id', tag_id);
            row.append($('<td class="select"></td>').html(select));
            row.append($('<td class="title"></td>').text(link.title));
            var direct = $('<a href="'+link.url+'"></a>').text(link.url);
            row.append($('<td class="url"></td>').html(direct));
            row.append($('<td class="tags"></td>').text(JSON.stringify(link.tags)));
            row.append($('<td class="active"></td>').text(JSON.stringify(link.active)));
            table.append(row);
        });
        ret_div.append(table);
    });
};

$(function() {
    //message bar
    $('a#bottom-pane-show').bind('click', function() {
        $.getJSON('/devices/messages', response => {
            var message_div = $('<div></div>');
            $.each(response.result, (dev_id, message) => {
                message_div.append($('<h3></h3>').text(dev_id));
                message_div.append($('<pre></pre>').text(message));
            });
            $('div#bottom-pane-content').html(message_div);
        });
    });

    //tags page
    $('a.tag-links').bind('click', function() {
        var tag_id = $(this).attr('data-link-id');
        if ($.togg_link_table(tag_id) && !$('div#'+tag_id+'-link-table').html())
            $.load_links(tag_id, null);
    });

    $('a.mo-sel-new').bind('click', function() {
        var tag_id = $(this).attr('data-link-id');
        var selected = $.selected(tag_id);
        if (selected.length) {
            var dev_select = $('select[data-link-id="'+tag_id+'"]').filter('.device-select');
            $.getJSON('/devices/', result => {
                $.each(result.devices, (_, dev_id) => {
                    dev_select.append($('<option></option>')
                                      .text(dev_id).attr('value', dev_id));
                });
            });
            var msg_btn = $('button[data-link-id="'+tag_id+'"]').filter('.make-message');
            msg_btn.attr('disabled', false);
            msg_btn.bind('click', function() {
                var device = dev_select.children('option:selected').val();
                selected = $.selected(tag_id);
                $.post('/devices/'+device+'/messages', {
                    message: 'open',
                    win_id: null,
                    tag: null,
                    link_ids: JSON.stringify(selected)
                }).done(function() {
                    $.deselect(tag_id);
                    //location.reload(true);
                    $('a#bottom-pane-show').click();
                });
            });
            dev_select.attr('disabled', false);
        }
    });

    //recent and active
    $("input[name='link']").change(function() {
        var selected = $.selected();
        if (selected.length) {
            $('div#bulk-edit').attr('style', 'display:block');
        } else {
            $('div#bulk-edit').attr('style', 'display:none');
        }
    });

    var link_table = {
        el: {
            visitCount: $('a.count'),
            tagList: $('a.tags'),
            linkTitle: $('a.title'),
            optionPanels: $('div.desc'),
            visitDayRange: $('span#day-range'),
        },

        init: function() {
            link_table.bindUI();
        },

        bindUI: function() {
            link_table.el.visitCount.on('click', link_table.showVisits);
            link_table.el.tagList.on('click', link_table.showTags);
            link_table.el.linkTitle.on('click', link_table.showDesc);
        },

        linkOptionPanel: function(link_id) {
            return link_table.el.optionPanels.filter('#' + link_id);
        },

        fillOptionPanel: function(link_id, elem) {
            link_table.linkOptionPanel(link_id).html(elem);
        },

        toggleOptionPanel: function(link_id, mode) {
            var optionPanel = link_table.linkOptionPanel(link_id);
            if (optionPanel.attr('data-showing') == mode) {
                optionPanel.attr('style', 'display:none');
                optionPanel.attr('data-showing', 'none');
                return false;
            } else {
                optionPanel.attr('style', 'display:block');
                optionPanel.attr('data-showing', mode);
                return true;
            }
        },

        showVisits: function(event) {
            function getVisits(link_id, days_back) {
                return $.getJSON('/recent/visits', {link_id: link_id,
                                                    days_back: days_back});
            }
            function showVisitPanel(data) {
                link_table.fillOptionPanel(data.link_id,
                                           $('<pre></pre>').text(data.result));
            }
            var link_id = event.target.getAttribute('data-link-id');
            if (link_table.toggleOptionPanel(link_id, 'visits'))
                getVisits(link_id, link_table.el.visitDayRange.text())
                    .then(showVisitPanel);
        },

        showTags: function(event) {
            function getTags(link_id) {
                return $.getJSON('/link/tags', {link_id: link_id, format: true});
            }
            function showTagPanel(data) {
                link_table.fillOptionPanel(data.link_id,
                                           $('<pre></pre>').text(data.result));
            }
            var link_id = event.target.getAttribute('data-link-id');
            if (link_table.toggleOptionPanel(link_id, 'tags')) {
                getTags(link_id).then(showTagPanel);
            }
        },

        showDesc: function(event) {
            function getData(link_id) {
                return $.getJSON('/link/' + link_id);
            }
            function getForm() {
                return $.get('/form/link_edit');
            }
            function saveLinkData(event) {
                var form = $(event.target);
                var link_id = form.attr('data-link-id');
                $.post('/link/'+link_id, form.serialize());//.done(_ => location.reload(true));
            }
            function showDescPanel(data) {
                var desc_form = getForm().then(form => {
                    var j_form = $(form);
                    j_form.attr('data-link-id', data.link_id);
                    j_form.children("input[name='title']").attr('value', data.title);
                    j_form.children("textarea[name='desc']").text(data.desc);
                    return j_form;
                });
                desc_form.then(e => {
                    e.submit(saveLinkData);
                    link_table.fillOptionPanel(data.link_id, e);
                });

            }
            var link_id = event.target.getAttribute('data-link-id');
            if (link_table.toggleOptionPanel(link_id, 'title')) {
                getData(link_id).then(showDescPanel);
            }
        },

    };

    var bulk_tb = {
        el: {
            container: $('div#bulk-edit'),

            deleteLinks: $('button#remove-links'),
            addTagsOpen: $('button#load-tag-add'),
            removeTagsOpen: $('button#load-tag-remove'),

            links: $("input[name='link']"),
            optionPanes: $('div.bulk-edit-pane'),
            optionSubmit: $('button#bulk-option-submit'),

            tagAddPane: $('div#tag-add'),
            tagAddSelect: $('select#sel-tag-add'),
            tagAddNew: $('input#new-tag'),

            tagRemovePane: $('div#tag-remove'),
            tagRemoveSelect: $('select#sel-tag-remove'),
        },

        init: function() {
            bulk_tb.bindUI();

        },

        bindUI: function() {
            bulk_tb.el.deleteLinks.on('click', bulk_tb.deleteLinks);
            bulk_tb.el.addTagsOpen.on('click', bulk_tb.focusTagsAdd);
            bulk_tb.el.removeTagsOpen.on('click', bulk_tb.focusTagsRemove);
        },

        deleteLinks: function() {
            function deleteLink(_, link_id) {
                $.ajax({url: '/link/'+link_id, type: 'DELETE'});
            }
            $.each(bulk_tb.selection(), deleteLink);
            location.reload(true);
        },

        addTags: function() {
            function addNewTag(tag_id) {
                return $.ajax({url: '/tag/'+tag_id, type: 'PUT'});
            }
            function addLinksToTag(tag_id, link_list) {
                return $.post('/links/tags', {
                    tag: tag_id, link_ids: JSON.stringify(link_list)
                });
            }
            var tag = bulk_tb.el.tagAddSelect.children('option:selected').val();
            if (!tag) return;
            var op = function() {};
            if (tag == 'NEW') {
                tag = bulk_tb.el.tagAddNew.val();
                if (tag)
                    op = addNewTag(tag).then(_ => addLinksToTag(tag, bulk_tb.selection()));
            } else
                op = addLinksToTag(tag, bulk_tb.selection());
            op.then(_ => location.reload(true));
        },

        removeTags: function() {
            var tag = bulk_tb.el.tagRemoveSelect.children('option:selected').val();
            if (!tag) return;

            $.ajax({url:'/links/tags', type: 'DELETE',
                    data: {tag: tag,
                           link_ids: JSON.stringify(bulk_tb.selection())
                          }}).done(_ => location.reload(true));
        },

        getTagList: function() {
            return $.getJSON('/tags/list', data => data.tags);
        },

        getCommonTags: function(linkid_list) {
            return $.getJSON('/links/tags',
                             {link_ids: JSON.stringify(linkid_list)},
                             function(data) {return data.tags;});
        },

        loadTagRemoveSelect: function(tags) {
            bulk_tb.el.tagRemoveSelect.html('');
            for (const tag of tags) {
                var option = $('<option></option>').text(tag).attr('value', tag);
                bulk_tb.el.tagRemoveSelect.append(option);
            }
        },

        loadTagAddSelect: function(tags, disabled_tags) {
            bulk_tb.el.tagAddSelect.html('');
            console.log(tags, disabled_tags);
            for (const tag of tags) {
                var option = $('<option></option>')
                    .text(tag.pre + tag.id).attr('value', tag.id);
                if (disabled_tags.includes(tag))
                    option.prop('disabled', true);
                bulk_tb.el.tagAddSelect.append(option);
            }
            bulk_tb.el.tagAddSelect.append('<option value="NEW">--New Tag--<\option>');
        },

        focusTagsRemove: function() {
            bulk_tb.getCommonTags(bulk_tb.selection()).then(res => {
                bulk_tb.loadTagRemoveSelect(res.tags);
            });
            bulk_tb.focusPane(bulk_tb.el.tagRemovePane);

            bulk_tb.el.optionSubmit.off('click');
            bulk_tb.el.optionSubmit.on('click', bulk_tb.removeTags);
        },

        focusTagsAdd: function() {
            bulk_tb.getTagList().then(res => {
                bulk_tb.getCommonTags(bulk_tb.selection()).then(common_res => {
                    bulk_tb.loadTagAddSelect(res.tags, common_res.tags);
                });
            });
            bulk_tb.focusPane(bulk_tb.el.tagAddPane);

            bulk_tb.el.tagAddSelect.on('change', bulk_tb.enableNewTag);

            bulk_tb.el.optionSubmit.off('click');
            bulk_tb.el.optionSubmit.on('click', bulk_tb.addTags);
        },

        enableNewTag: function() {
            if (bulk_tb.el.tagAddSelect.children('option:selected').val() == 'NEW') {
                bulk_tb.el.tagAddNew.prop('value', '');
                bulk_tb.el.tagAddNew.prop('disabled', false);
            } else {
                bulk_tb.el.tagAddNew.prop('disabled', true);
                bulk_tb.el.tagAddNew.prop('value', '');
            }
        },

        focusPane: function(pane) {
            bulk_tb.hidePanes();
            pane.attr('style', 'display:block');
        },

        hidePanes: function() {
            $.each(bulk_tb.el.optionPanes, (_, elem) => {
                elem.setAttribute('style', 'display:none');
            });
        },

        selection: function() {
            var selected = [];
            $.each(bulk_tb.el.links.filter(":checked"), function() {
                selected.push($(this).val());
            });
            return selected;
        },

        clear_selection: function() {
            $.each(bulk_tb.el.links.filter(":checked"), function() {
                $(this).prop('checked', false);
            });
        },
    };
    link_table.init();
    bulk_tb.init();
});
