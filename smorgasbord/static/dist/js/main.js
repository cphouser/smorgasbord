

$.deselect = function() {
    $.each($("input[name='link']:checked"), function() {
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

$.togg_link_pane = function(link_id, mode) {
    if ($('div#'+link_id).attr('data-showing') == mode) {
        $('div#'+link_id).attr('style', 'display:none');
        $('div#'+link_id).attr('data-showing', 'none');
        return false;
    } else {
        $('div#'+link_id).attr('style', 'display:block');
        $('div#'+link_id).attr('data-showing', mode);
        return true;
    }
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
            //var title = $('<input type="text" name="title">')
            //    .attr('value', data.title);
            //var desc = $('<textarea rows=3 name="desc">')
            //    .attr('value', data.desc);
            //form.append(title);
            //form.append('<button type="submit">Edit Link</button>');
            //form.append($('<br>'));
            //form.append(desc);
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
        if ($.togg_link_table(tag_id))
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
                    //$.deselect();
                    //location.reload(true);
                    $('a#bottom-pane-show').click();
                });
            });
            dev_select.attr('disabled', false);
        }
    });

    //recent and active
    $('a.count').bind('click', function() {
        var link_id = $(this).attr('data-link-id');
        if ($.togg_link_pane(link_id, 'visits'))
            $.getJSON('/recent/visits', {
                link_id: link_id,
                days_back: $('#day-range').text()
            }, function(data) {
                var pre = $('<pre></pre>').text(data.result);
                $('div#'+link_id).html(pre);
            });
        return false;
    });

    $('a.tags').bind('click', function() {
        var link_id = $(this).attr('data-link-id');
        if ($.togg_link_pane(link_id, 'tags'))
        $.getJSON('/link/tags', {
            link_id: link_id,
            format: true
        }, function(data) {
            var pre = $('<pre></pre>').text(data.result);
            $('div#'+link_id).html(pre);
        });
        return false;
    });

    $('a.title').bind('click', function() {
        var link_id = $(this).attr('data-link-id');
        if ($.togg_link_pane(link_id, 'title'))
            $.getJSON('/link/' + link_id, function(data) {
                var form = $('<form></form>').text(data.result);
                form.attr('class', 'link-edit-text');
                form.attr('data-link-id', data.link_id);
                var title = $('<input type="text" name="title">')
                    .attr('value', data.title);
                var desc = $('<textarea rows=3 name="desc">')
                    .attr('value', data.desc);
                form.append(title);
                form.append('<button type="submit">Edit Link</button>');
                form.append($('<br>'));
                form.append(desc);
                $('div#'+data.link_id).html(form);
            });
    });

    $("input[name='link']").change(function() {
        var selected = $.selected();
        if (selected.length) {
            $('div#bulk-edit').attr('style', 'display:block');
        } else {
            $('div#bulk-edit').attr('style', 'display:none');
        }
    });

    $('#remove-links').bind('click', function() {
        var selected = $.selected();
        $.each(selected, function(_, link_id) {
            $.ajax({url: '/link/'+link_id, type: 'DELETE'});
        });
        $.deselect();
        location.reload(true);
    });

    $('#load-tag-edit').bind('click', function() {
        var selected = $.selected();
        var common_tags = [];
        $.getJSON('/links/tags', {
            link_ids: JSON.stringify(selected),
        }, function(data) {
            var tags = [];
            $('select#sel-tag-remove').html("");
            $.each(data.tags, function(_, tag) {
                var option = $('<option></option>')
                    .text(tag).attr('value', tag);
                $('select#sel-tag-remove').append(option);
                common_tags.push(tag);
            });
        });
        $.getJSON('/tags/list', function(data) {
            $('select#sel-tag-add').html('');
            $.each(data.tags, function(_, tag) {
                var option = $('<option></option>')
                    .text(tag.pre + tag.id).attr('value', tag.id);
                if (common_tags.includes(tag.id))
                    option.prop('disabled', true);
                $('select#sel-tag-add').append(option);
            });
            $('select#sel-tag-add').append(
                '<option value="NEW">--New Tag--<\option>'
            );
        });
        if ($('#bulk-tag-edit').attr('style') == 'display:none')
            $('#bulk-tag-edit').attr('style', 'display:block');
        return false;
    });

    $('select#sel-tag-add').change(function() {
        if ($(this).children('option:selected').val() == 'NEW')
            $('input#new-tag').prop('disabled', false);
        else {
            $('input#new-tag').prop('disabled', true);
            $('input#new-tag').prop('value', '');
        }
    });

    $('#btn-tag-add').bind('click', function(event) {
        var selected = $.selected();
        var tag = $('select#sel-tag-add').children('option:selected').val();
        if (!tag) {
            return;
        }
        if (tag == 'NEW') {
            tag = $('input#new-tag').val();
            if (!tag) {
                return;
            } else
                $.ajax({url: '/tag/'+tag, type: 'PUT'}).done(function() {
                    $.post('/links/tags', {
                        tag: tag, link_ids: JSON.stringify(selected)
                    }).done(function() {
                        $.deselect();
                        location.reload(true);
                    });
                });
        } else {
            $.post('/links/tags', {
                tag: tag, link_ids: JSON.stringify(selected)
            }).done(function() {
                $.deselect();
                location.reload(true);
            });
        }
    });

    $('#btn-tag-remove').bind('click', function(event) {
        var selected = $.selected();
        var tag = $('select#sel-tag-remove').children('option:selected').val();
        if (!tag) {
            event.preventDefault();
            return;
        }
        $.ajax({url:'/links/tags', type: 'DELETE',
                data: {tag: tag, link_ids: JSON.stringify(selected)}
               }).done($.deselect());

        location.reload(true);
    });

});
