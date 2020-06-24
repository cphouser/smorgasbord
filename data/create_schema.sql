CREATE TABLE if not exists links(
       link_id text primary key,
       url text unique,
       matching text unique,
       title text,
       description text,
       parent text,
       foreign key (parent) references link(link_id)
               on delete set null on update no action);

create table if not exists visits(
       link_id text not null,
       visit_ts text not null,
       visit_td text,
       primary key (link_id, visit_ts),
       foreign key (link_id) references links(link_id)
               on delete cascade on update no action);

create table if not exists tags(
       tag_id text primary key,
       description text,
       parent text,
       foreign key (parent) references tags(tag_id)
               on delete cascade on update no action);

create table if not exists link_tags(
       link_id text not null,
       tag_id text not null,
       primary key (link_id, tag_id),
       foreign key (link_id) references links(link_id)
               on delete cascade on update no action,
       foreign key (tag_id) references tags(tag_id)
               on delete cascade on update no action);

create table if not exists windows(
       win_id text primary key,
       browser_id integer);

create table if not exists window_links(
       link_id text not null,
       win_id text not null,
       visit_ts text not null,
       visit_td text not null,
       foreign key (win_id) references windows(win_id)
               on delete cascade on update no action);

create table if not exists device_windows(
       win_id text not null,
       dev_id text,
       unique (win_id, dev_id),
       foreign key (dev_id) references devices(dev_id)
               on delete cascade on update no action,
       foreign key (win_id) references windows(win_id)
               on delete cascade on update no action);

create table if not exists devices(
       dev_id text primary key);


-- create trigger if not exists window_exists
--     before insert on window_links
-- begin
--   select
--     case
--          when new.win_id not in (select win_id from windows) then
--               raise (ABORT, 'Window does not exist') end;
-- end;
