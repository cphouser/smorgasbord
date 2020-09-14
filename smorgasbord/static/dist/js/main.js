

$.deselect = function() {
    $.each($("input[name='link']:checked"), function() {
        $(this).prop('checked', false);
    });
};

$.selected = function() {
    var selected = [];
    $.each($("input[name='link']:checked"), function() {
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

$(function() {
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
