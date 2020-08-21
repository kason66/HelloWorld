--DROP TABLE IF EXISTS user;
--DROP TABLE IF EXISTS post;
DROP table IF EXISTS favours;
DROP table IF EXISTS comments;
DROP table IF EXISTS tags;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  tags TEXT DEFAULT NULL,
  imgs TEXT default Null,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE favours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    createdTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    createdTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level INTEGER NOT NULL default 1,
    parent_id INTEGER NOT NULL default 0,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

create table imgs(
    id integer primary key autoincrement ,
    name text not null ,
    url text not null ,
    created TIMESTAMP not null default CURRENT_TIMESTAMP
);

insert into tags (name) values ("life");
insert into tags (name) values ("study");
insert into tags (name) values ("work");
insert into tags (name) values ("other");

commit ;