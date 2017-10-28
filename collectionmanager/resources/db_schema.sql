-- Script to create the database schema

CREATE TABLE directory (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE
);

CREATE TABLE path (
    id INTEGER PRIMARY KEY,
    directory_id INTEGER,
    relative_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    FOREIGN KEY(directory_id) REFERENCES directory(id) ON DELETE CASCADE
);
