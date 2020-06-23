
import apsw

import orgparse
import zlib
from datetime import datetime

# sqlite> pragma table_info('link_tags');
# cid         name        type        notnull     dflt
# ----------  ----------  ----------  ----------  ----
# 0           link_id     text        1
# 1           tag_id      text        1
# sqlite> pragma table_info('links');
# cid         name        type        notnull     dflt
# ----------  ----------  ----------  ----------  ----
# 0           link_id     text        0
# 1           url         text        0
# 2           matching    text        0
# 3           title       text        0
# 4           descriptio  text        0
# 5           parent      text        0
# sqlite> pragma table_info('visits');
# cid         name        type        notnull     dflt
# ----------  ----------  ----------  ----------  ----
# 0           link_id     text        1
# 1           visit_ts    text        1
# 2           visit_td    text        0
# sqlite> pragma table_info('tags');
# cid         name        type        notnull     dflt
# ----------  ----------  ----------  ----------  ----
# 0           tag_id      text        0
# 1           descriptio  text        0
# 2           parent      text        0


class OrgTables():
    def __init__(self):
        # link_id: (url, title, parent)
        self.links = {}
        # (link_id, visit_ts)
        self.visits = []
        # (tag_id, parent)
        self.category = []
        # (link_id, tag_id)
        self.link_category = []

    def insert_links(self, cursor):
        for link_id, (url, title, parent) in self.links.items():
            cursor.execute('insert into links(link_id, url, title, parent)'
                           'values(?,?,?,?)', (link_id, url, title, parent))

    def insert_visits(self, cursor):
        for (link_id, visit_ts) in self.visits:
            time_string = visit_ts.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('insert into visits(link_id, visit_ts)'
                           'values(?,?)', (link_id, time_string))

    def insert_tags(self, cursor):
        for (tag_id, parent) in self.category:
            cursor.execute('insert into tags(tag_id, parent) values(?,?)',
                           (tag_id, parent))

    def insert_linktags(self, cursor):
        for (link_id, tag_id) in self.link_category:
            cursor.execute('insert into link_tags(link_id, tag_id) values(?,?)',
                           (link_id, tag_id))

    def load_orgparse(self, org_struct):
        window_categories = {}
        def recursive_load(org_node, link_parent=None, cat_parent=None):
            if 'URL' in org_node.properties:
                link_id = OrgTables.link_id(org_node.properties['URL'])
                self.add_link(link_id, org_node.properties['URL'],
                              org_node.heading, link_parent)

                if 'CTIME' in org_node.properties:
                    ctime = datetime.strptime(org_node.properties['CTIME'],
                                              '%Y-%m-%d %H:%M:%S')
                    if 'OTIME' in org_node.properties:
                        otime = datetime.strptime(org_node.properties['OTIME'],
                                                  '%Y-%m-%d %H:%M:%S')
                        if (ctime != otime):
                            self.add_visit(link_id, otime)
                    self.add_visit(link_id, ctime)
                elif 'OTIME' in org_node.properties:
                    otime = datetime.strptime(org_node.properties['OTIME'],
                                              '%Y-%m-%d %H:%M:%S')
                    self.add_visit(link_id, otime)
                else:
                    print("no date for", link_id, org_node.properties['URL'])
                if (cat_parent is not None
                    and (link_id, cat_parent) not in self.link_category):
                    self.link_category.append((link_id, cat_parent))
                if len(org_node.shallow_tags) > 0:
                    for window in org_node.shallow_tags:
                        if window in window_categories:
                            window_categories[window].append(link_id)
                        else:
                            window_categories[window] = [link_id]
                if len(org_node.children) > 0:
                    #print(link_parent, '->', link_id)
                    [recursive_load(child, link_id, cat_parent)
                     for child in org_node.children]
            else:
                cat_id = org_node.heading.strip().lower().replace(' ','_')
                self.category.append((cat_id, cat_parent))
                #print("category:", cat_parent, '->', cat_id)
                if len(org_node.children) > 0:
                    [recursive_load(child, cat_parent=cat_id)
                     for child in org_node.children]

        for node in org_struct.children:
            recursive_load(node)

        for window, id_list in window_categories.items():
            cat_id = window.strip().lower().replace(' ','_')
            self.category.append((cat_id, None))
            for link_id in id_list:
                self.link_category.append((link_id, cat_id))


    def add_visit(self, link_id, v_time):
        if (link_id, v_time) not in self.visits:
            self.visits.append((link_id, v_time))

    def add_link(self, link_id, url, title=None, parent=None):
        if title is None:
            title = url
        if link_id not in self.links:
            self.links[link_id] = (url, title, parent)
        elif self.links[link_id][0] != url:
            print('hash collision?')

    @staticmethod
    def link_id(url):
        chk_str = format(zlib.crc32(url.encode('ascii')), 'x')
        start_idx = url.find(':') + 1
        while(url[start_idx] == '/'):
            start_idx = start_idx + 1
        end_idx = url.find('/', start_idx)
        return chk_str.rjust(8, '0') + url[start_idx:end_idx].replace('.', '')


# org = orgparse.load('/home/xeroxcat/Dropbox/org/brain/webpages.org')
# orgTables = OrgTables()
# orgTables.load_orgparse(org)
# orgTables.insert_linktags(cursor)

connection = apsw.Connection('smorgasbord.db')
cursor = connection.cursor()

connection.close()


#cursor.execute('create table foo(x,y,z)')
#cursor.execute('insert into foo values(?,?,?)', (1, 1.1, None))

#for x, y, z in cursor.execute('select x, y, z from foo'):
#    print(cursor.getdescription())
#    print(x, y, z)
