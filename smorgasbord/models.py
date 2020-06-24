"""Data Models"""
from . import db

class Link(db.Model):

    __tablename__ = 'links'
    __table_args__ = {'extend_existing': True}

    id = db.Column('link_id', db.String(), primary_key=True)
    url = db.Column('url', db.String(), unique=True)
    match = db.Column('matching', db.String(), unique=True)
    title = db.Column('title', db.String())
    description = db.Column('description', db.String())
    parent = db.Column('parent', db.String(), db.ForeignKey('links.link_id'))


class Visit(db.Model):

    __tablename__ = 'visits'
    __table_args__ = {'extend_existing': True}

    link_id = db.Column('link_id', db.String(), db.ForeignKey('links.link_id'),
                        primary_key=True)
    time = db.Column('visit_ts', db.String(), primary_key=True)
    duration = db.Column('visit_td', db.String())


class Tag(db.Model):

    __tablename__ = 'tags'
    __table_args__ = {'extend_existing': True}

    id = db.Column('tag_id', db.String(), primary_key=True)
    description = db.Column('description', db.String())
    parent = db.Column('parent', db.String(), db.ForeignKey('tags.id'))

link_tags = db.Table('link_tags',
                     db.Column('link_id', db.String(),
                               db.ForeignKey('links.link_id'),
                               primary_key=True),
                     db.Column('tag_id', db.String(),
                               db.ForeignKey('tags.tag_id'),
                               primary_key=True),
                     extend_existing=True)

device_windows = db.Table('device_windows',
                          db.Column('win_id', db.String(),
                                    db.ForeignKey('windows.win_id'),
                                    nullable=False),
                          db.Column('dev_id', db.String(),
                                    db.ForeignKey('devices.dev_id')),
                          db.UniqueConstraint('win_id', 'dev_id'),
                          extend_existing=True)


class WindowLinks(db.Model):

    __tablename__ = 'window_links'
    __table_args__ = {'extend_existing': True}

    win_id = db.Column('win_id', db.String(),
                       db.ForeignKey('windows.win_id'), nullable=False,
                       primary_key=True)
    link_id = db.Column('link_id', db.String(), nullable=False,
                        primary_key=True)
    time = db.Column('visit_ts', db.String(), nullable=False, primary_key=True)
    duration = db.Column('visit_td', db.String(), nullable=False)


class Window(db.Model):

    __tablename__ = 'windows'
    __table_args__ = {'extend_existing': True}

    bid = db.Column('browser_id', db.Integer)
    id = db.Column('win_id', db.String(), primary_key=True)

class Device(db.Model):

    __tablename__ = 'devices'
    __table_args__ = {'extend_existing': True}

    id = db.Column('dev_id', db.String(), primary_key=True)
    windows = db.relationship('Window', secondary=device_windows,
                              lazy='subquery', backref=db.backref('devices',
                                                                  lazy=True))
