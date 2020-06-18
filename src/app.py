#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# heavily adapted from dash interactive visualization demo by jiahui wang
# https://github.com/jhwang1992/network-visualization
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

import pandas as pd
from colour import Color
from datetime import datetime, date, timedelta, time
from textwrap import dedent as d
import json
import apsw
from zlib import crc32
from numpy import interp, add

class TimeToDist:
    sec_interval = 0;#float of one second offset
    day_interval = 0;#float of one day offset

    @classmethod
    def setIntervals(cls, day_sorted_set):
        def date_float(date):
            return datetime.combine(date, datetime.min.time()).timestamp()
        min_day = date_float(day_sorted_set[0])
        max_day = date_float(day_sorted_set[-1])
        cls.day_interval = interp(date_float(day_sorted_set[0] +
                                             timedelta(days=1)),
                                  [min_day, max_day], [0,1])
        cls.sec_interval = cls.day_interval / 86400
        return {day: (0,interp(date_float(day), [min_day, max_day], [0,1]))
                for day in day_sorted_set}

    @classmethod
    def timeOffset(cls, date_time):
        time = date_time.time()
        seconds = (time.hour * 60 + time.minute) * 60 + time.second
        return cls.sec_interval * seconds


class NetworkLayout:
    def __init__(self, input_dict, spacing=0.015, max_offset=0.2):
        self.pos_dict = dict(input_dict)
        inv_pos_dict = self.invert_dict(input_dict)
        wrap_index = int(max_offset / spacing)
        for (x,y), nodes in inv_pos_dict.items():
            if len(nodes) > 1:
                sorted_nodes = sorted(nodes, reverse=True)
                for i in range(len(nodes)):
                    x_off = (i % wrap_index) * spacing
                    y_off = (int(i / wrap_index) * spacing * 0.7
                             + ((wrap_index - (i % wrap_index)) * spacing * 0.2))
                    print(x_off, y_off)
                    self.pos_dict[sorted_nodes[i]] = (x - x_off, y - y_off)

    def asDict(self):
        return self.pos_dict

    @staticmethod
    def invert_dict(to_invert):
        inv_dict = {}
        for k, v in to_invert.items():
            inv_dict[v] = inv_dict.get(v, [])
            inv_dict[v].append(k)
        return inv_dict


class TimeRange:
    def __init__(self):
        connection = apsw.Connection(DB_FILE)
        visit_df = pd.read_sql_query('select visit_ts from visits',
                                     connection, parse_dates=['visit_ts'])
        connection.close()
        self.start = visit_df['visit_ts'].min()
        self.end = datetime.combine((visit_df['visit_ts'].max()
                                     + timedelta(days=1)).date(),
                                    time.min)
        date_list = [self.end]
        date_list.append(self.end - timedelta(days=1))
        date_list.append(self.end - timedelta(days=3))
        date_list.append(self.end - timedelta(weeks=1))
        date_list.append(self.end - timedelta(weeks=2))
        date_list.append(self.end.replace(month=(12 if self.end.month==1
                                                  else self.end.month - 1),
                                          year=(self.end.year - 1
                                                if self.end.month == 1
                                                else self.end.year)))
        date_list.append(self.end.replace(month=((self.end.month + 9)
                                                  if self.end.month < 4
                                                  else self.end.month - 3),
                                          year=(self.end.year - 1
                                                if self.end.month < 4
                                                else self.end.year)))
        date_list.append(self.end.replace(month=((self.end.month + 6)
                                                  if self.end.month < 7
                                                  else self.end.month - 6),
                                          year=(self.end.year - 1
                                                if self.end.month < 7
                                                else self.end.year)))
        date_list.append(self.end - timedelta(weeks=52))
        while (date_list[-1] > self.start):
            date_list.append(date_list[-1] - timedelta(weeks=52))
        self.marks = list(reversed(date_list))

    def sliderDate(self, idx):
        if len(self.marks) <= idx or idx < 0:
            return None
        else:
            return self.marks[idx]

    def marksDict(self):
        return {i: {'label': ts.strftime('%d%b%Y')}
                for i, ts in enumerate(self.marks)}

    def rangeMax(self):
        return len(self.marks) - 1


class ColorMap:
    def __init__(self, bound1='000000', bound2='FFFFFF'):
        self.bound1 = self.hexStrTo3Tup(bound1)
        self.bound2 = self.hexStrTo3Tup(bound2)

    def color(self, value):
        numeric = format(crc32(value.encode('ascii')),'x').zfill(8)[:6]
        r1, g1, b1 = self.bound1
        r2, g2, b2 = self.bound2
        r_rand = int('0x' + numeric[:2], 0)
        g_rand = int('0x' + numeric[2:4], 0)
        b_rand = int('0x' + numeric[4:6], 0)
        r = int(interp(r_rand, [0,255], [r1, r2]))
        g = int(interp(g_rand, [0,255], [g1, g2]))
        b = int(interp(b_rand, [0,255], [b1, b2]))
        return ('#' + hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2)
                + hex(b)[2:].zfill(2))

        #print(self.bound1, self.bound2)

    @staticmethod
    def hexStrTo3Tup(hex_str):
        r = int('0x' + hex_str.zfill(6)[:2], 0)
        g = int('0x' + hex_str.zfill(6)[2:4], 0)
        b = int('0x' + hex_str.zfill(6)[4:6], 0)
        return (r, g, b)


def timeline_graph(dateRange, selected=None):
    def space_tags(tag_dict, tag_offset=0.5):
        def percolate_depth(tag_id, inherited_depth):
            if tag_id is None:
                #print('END')
                return 1
            #print(tag_id, end=' : ')
            if inherited_depth > tag_dict[tag_id]['depth']:
                tag_dict[tag_id]['depth'] = inherited_depth
                depth = percolate_depth(tag_dict[tag_id]['parent'],
                                       inherited_depth + 1)
            else:
                #print('MERGE')
                depth = tag_dict[tag_id]['depth']
            return depth

        def recursive_parent(tag_id):
            for parent in cursor.execute(
                    f'select parent from tags where tag_id="{tag_id}"'):
                par_id = parent[0]
                if par_id is None:
                    return
                else:
                    tag_dict[tag_id]['parent'] = par_id
                    if par_id not in tag_dict:
                        tag_dict[par_id] = dict(
                            depth=tag_dict[tag_id]['depth']+1, parent=None)
                        recursive_parent(par_id)

        max_depth = 1
        connection = apsw.Connection(DB_FILE)
        cursor = connection.cursor()
        #print(tag_dict.keys())
        child_list = list(tag_dict.keys())
        for tag in child_list:
            recursive_parent(tag)
        for tag in child_list:
            print(tag, end=' : ')
            max_depth = max([percolate_depth(tag_dict[tag]['parent'],
                                             tag_dict[tag]['depth'] + 1),
                             max_depth])
        print(max_depth)
        #print(max_depth)
        for tag in tag_dict:
            tag_dict[tag]['x_off'] = interp(tag_dict[tag]['depth'],
                                            [0, max_depth], [0, tag_offset])
            print(tag_dict[tag]['depth'], str(tag_dict[tag]['x_off'])[:5], tag,
                  '->', tag_dict[tag]['parent'])
        connection.close()


    date_0 = timerange.sliderDate(dateRange[0])
    date_1 = timerange.sliderDate(dateRange[1])

    connection = apsw.Connection(DB_FILE)
    if selected is not None:
        node_type = selected['n_type']
        if node_type == 'link':
            visit_df = pd.read_sql_query(
                'select link_id, visit_ts, visit_td, tag_id, title, url '
                'from links join visits using (link_id) left join link_tags '
                f'using (link_id) where visit_ts >= "{date_0}" and '
                f'visit_ts <= "{date_1}" and link_id = "{selected["name"]}"',
                connection, parse_dates=['visit_ts'],
                index_col='visit_ts')
        elif node_type == 'tag':
            visit_df = pd.read_sql_query(
                'select link_id, visit_ts, visit_td, tag_id, title, url '
                'from links join visits using (link_id) left join link_tags '
                f'using (link_id) where visit_ts >= "{date_0}" and '
                f'visit_ts <= "{date_1}" and tag_id = "{selected["name"]}"',
                connection, parse_dates=['visit_ts'],
                index_col='visit_ts')
        elif node_type == 'day':
            visit_df = pd.read_sql_query(
                'select link_id, visit_ts, visit_td, tag_id, title, url '
                'from links join visits using (link_id) left join link_tags '
                'using (link_id) where visit_ts >= '
                f'"{date_0}" and visit_ts <= "{date_1}"',
                connection, parse_dates=['visit_ts'],
                index_col='visit_ts')
    else:
        # Query for all visited links and associated tags in visit range
        visit_df = pd.read_sql_query(
            'select link_id, visit_ts, visit_td, tag_id, title, url '
            'from links join visits using (link_id) left join link_tags '
            'using (link_id) where visit_ts >= '
            f'"{date_0}" and visit_ts <= "{date_1}"',
            connection, parse_dates=['visit_ts'],
            index_col='visit_ts')
    connection.close()

    # find days of visits in dataframe
    visit_df['day'] = visit_df.apply(lambda row: row.name.date(), axis=1)
    visit_df.sort_index(inplace=True, ascending=False)

    # set coordinates for dates - distribute from 0 to 1 along y axis
    # get date node coordinates as dict and initialize TimeToDist intervals
    # to offset link nodes by time of last visit
    days = sorted(set(visit_df['day']))
    xy_dict = TimeToDist.setIntervals(days)

    # initialize networkX graph with day->link edges
    G = nx.from_pandas_edgelist(visit_df, 'day', 'link_id', 'visit_td',
                                create_using=nx.DiGraph())

    # create dict of all associated tags, their parents, and the x-offset
    # from the most recently visited associated link node
    tags = {tag: dict(depth=1,parent=None) for tag in set(visit_df['tag_id'])}
    space_tags(tags)# generates field 'x_off'

    # add tag nodes to graph. get coordinates for link nodes and tags, aligned
    # horizontally w/ most recently visited child, and store in xy_dict.
    for visit_ts, link_id, _, tag_id, title, url, visit_day in \
            visit_df.itertuples():
        # skip if link data has been added from a more recent visit
        if link_id in xy_dict:
            continue

        G.nodes[link_id]['url'] = url
        G.nodes[link_id]['title'] = title

        # offset vertical position by time value of visit, store link position
        link_xy = tuple(add(xy_dict[visit_day],
                            (0.5, TimeToDist.timeOffset(visit_ts))))
        xy_dict[link_id] = link_xy

        # if tag is not yet in dict, add it w/ all parents not yet added
        # to graph and position dict. connect each to its parent w/ an edge
        if tag_id not in xy_dict:
            tag_xy = tuple(add(xy_dict[link_id], (tags[tag_id]['x_off'], 0)))
            xy_dict[tag_id] = tag_xy
            this_tag = tag_id
            parent = tags[tag_id]['parent']
            while parent is not None:
                #print(this_tag, '->', parent)
                G.add_edge(this_tag, parent)
                if parent in xy_dict:
                    break
                tag_xy = tuple(add(xy_dict[link_id],
                                   (tags[parent]['x_off'], 0)))
                xy_dict[parent] = tag_xy
                this_tag = parent
                parent = tags[parent]['parent']
        G.add_edge(link_id, tag_id)

    # generate layout as position dict
    # space nodes with networkX
    #pos = nx.drawing.layout.spring_layout(G,
    #                                      pos=NetworkLayout(xy_dict).asDict(),
    #                                      fixed=days, k=0.03, threshold=0.8)
    # or manually space
    pos = NetworkLayout(xy_dict).asDict()

    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    traceRecode = []
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        x_range = x1 - x0
        y_range = y1 - y0
        rx0 = x0 + (x_range / 3)
        ry0 = y0 + (y_range / 9)
        lx1 = x1 - (x_range / 3)
        ly1 = y1 - (y_range / 9)
        #weight
        trace = go.Scatter(x=tuple([x0, rx0, lx1, x1, None]),
                           y=tuple([y0, ry0, ly1, y1, None]),
                           mode='lines',# line={'width': weight},
                           marker=dict(color=colormap.color(edge[1])),
                           text='', hoverinfo='skip',
                           line_shape='spline', opacity=1)
        traceRecode.append(trace)

    for node in G.nodes():
        text = ''
        hovertext = ''
        if isinstance(node, date):
            text = str(node)
            custom_data = tuple([dict(type='day')])
        elif 'title' in G.nodes[node]:
            hovertext = G.nodes[node]['title']
            custom_data = tuple([dict(type='link', url=G.nodes[node]['url'])])
        else:
            hovertext = str(node)
            custom_data = tuple([dict(type='tag')])
        x, y = G.nodes[node]['pos']
        trace = go.Scatter(x=tuple([x]), y=tuple([y]),
                           hovertext=tuple([hovertext]), text=tuple([text]),
                           ids=tuple([node]), mode='markers+text',
                           customdata=custom_data, textposition='middle left',
                           hoverinfo='text',
                           marker={'size': 6,
                                   'color': (colormap.color(node)
                                             if not isinstance(node, date)
                                             else 'Black')})
        traceRecode.append(trace)

    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='', showlegend=False, hovermode='closest',
                            margin={'b': 10, 'l': 80, 'r': 10, 't': 10},
                            xaxis={'showgrid': False, 'zeroline': False,
                                   'showticklabels': False,
                                   'range':[-0.13,1.15],
                                   'fixedrange':True},
                            yaxis={'showgrid': False, 'zeroline': False,
                                   'showticklabels': False,
                                   'fixedrange':False},
                            height=800, clickmode='event+select',
                            annotations=[
                                dict(ax=(G.nodes[edge[0]]['pos'][0]
                                         + G.nodes[edge[1]]['pos'][0]) / 2,
                                     ay=(G.nodes[edge[0]]['pos'][1]
                                         + G.nodes[edge[1]]['pos'][1]) / 2,
                                     axref='x', ayref='y',
                                     x=(G.nodes[edge[1]]['pos'][0]
                                        + G.nodes[edge[0]]['pos'][0]) / 2,
                                     y=(G.nodes[edge[1]]['pos'][1]
                                        + G.nodes[edge[0]]['pos'][1]) / 2,
                                     xref='x', yref='y', text='',
                                     showarrow=False, opacity=1)
                                for edge in G.edges])}

    return figure


app = dash.Dash(__name__)
app.title = 'smorgasbord'
DB_FILE = 'smorgasbord.db'

# query the database to initialize time range
timerange = TimeRange()
TIME_RANGE=[timerange.rangeMax() - 1, timerange.rangeMax()]

# styles: for right side hover/click component
styles = {'pre': {'border': 'thin lightgrey solid', 'overflowX': 'scroll'}}
colormap = ColorMap('880033','ff88ff')

app.layout = html.Div([
    html.Div([html.H1("smorgasbord")], className="row"),
    html.Div(className="row",
        children=[
            html.Div(
                className="one column",
                children=[
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='time-range-slider', min=0,
                                max=timerange.rangeMax(),
                                vertical=True, step=1, value=TIME_RANGE,
                                marks=timerange.marksDict()),
                            html.Br(),
                            html.Div(id='output-container-range-slider')])]),
            html.Div(className="eight columns",
                     children=[dcc.Graph(
                         id="my-graph", figure=timeline_graph(TIME_RANGE),
                         config=dict(displayModeBar=False))]),
            html.Div(
                className="three columns",
                children=[
                    html.Div(className="twelve columns",
                             children=["center on node",
                                       dcc.Input(id="input1", type="text",
                                                 placeholder="link"),
                                       html.Div(id="output",
                                       )]),
                    html.Div(className='twelve columns', id='hover-data',
                             children=['hover over a node'],
                             style={'overflow-wrap': 'break-word',
                                    'height': '150px'}),
                    html.Div(className='twelve columns',
                             children=['click data', html.Pre(id='click-data',
                                          style=styles['pre'])],
                             style={'height': '300px'})])])])

@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('time-range-slider', 'value'),
    dash.dependencies.Input('my-graph', 'clickData')])
def update_graph(value, clickData):
    TIME_RANGE = value
    if (clickData is None or 'points' not in clickData
        or not len(clickData['points'])):
        selected_node = None
    else:
        node = clickData['points'][0]
        selected_node = dict(name=node['id'], n_type=node['customdata']['type'])
    return timeline_graph(TIME_RANGE, selected_node)

@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    if (hoverData is None or 'points' not in hoverData
        or not len(hoverData['points'])):
        return ['hover over a node for info']
    node = hoverData['points'][0]
    custom_data = node['customdata']
    node_type = custom_data['type']
    node_id = node['id']
    content = [node_type + ' node', html.Br()]
    if node_type in ['link', 'tag']:
        content.append(node['hovertext'])
    if node_type == 'link':
        content.append(html.Br())
        content.append(custom_data['url'])
    elif node_type == 'day':
        content.append(node['text'])

    return content

@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('my-graph', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)

#@app.callback(
#    dash.dependencies.Output('my-graph', 'figure'),
#    [dash.dependencies.Input('my-graph', 'clickData')])
#def display_click_data(clickData):
#    if (clickData is None or 'points' not in clickData
#        or not len(clickData['points'])):
#        print(clickdata)
#        selected_node = None
#    node = clickData['points'][0]
#    selected_node = dict(name=node['id'], n_type=node['customdata']['type'])
#    print(selected_node)
#    return timeline_graph(TIME_RANGE, selected_node)

if __name__ == '__main__':
    app.run_server(debug=True)
