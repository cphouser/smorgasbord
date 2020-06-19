CREATE TABLE links(
       link_id text primary key,
       url text unique,
       matching text unique,
       title text,
       description text,
       parent text,
       foreign key (parent) references link(link_id)
               on delete set null on update no action);

create table visits(
       link_id text not null,
       visit_ts text not null,
       visit_td text,
       primary key (link_id, visit_ts),
       foreign key (link_id) references links(link_id)
               on delete cascade on update no action);

create table tags(
       tag_id text primary key,
       description text,
       parent text,
       foreign key (parent) references tags(tag_id)
               on delete cascade on update no action);

create table link_tags(
       link_id text not null,
       tag_id text not null,
       primary key (link_id, tag_id)
       foreign key (link_id) references links(link_id)
               on delete cascade on update no action,
       foreign key (tag_id) references tags(tag_id)
               on delete cascade on update no action);
