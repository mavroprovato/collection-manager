-- Script to create the database schema

CREATE TABLE directory (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE
);

CREATE TABLE artist (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE album (
    id INTEGER PRIMARY KEY,
    artist_id INTEGER,
    name TEXT,
    year INTEGER,
    FOREIGN KEY(artist_id) REFERENCES artist(id) ON DELETE CASCADE
);

CREATE TABLE track (
    id INTEGER PRIMARY KEY,
    directory_id INTEGER,
    album_id INTEGER,
    name TEXT,
    number INTEGER,
    file_name TEXT NOT NULL,
    FOREIGN KEY(directory_id) REFERENCES directory(id) ON DELETE CASCADE,
    FOREIGN KEY(album_id) REFERENCES album(id) ON DELETE CASCADE
);
