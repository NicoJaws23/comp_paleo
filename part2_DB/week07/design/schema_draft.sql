-- schema_draft.sql
-- Proyecto Primates Geographic and Behavioral Database
-- Week 7 Assignment, Nico Jaworski

  DROP TABLE IF EXISTS observersamples;
  DROP TABLE IF EXISTS individuals;
  DROP TABLE IF EXISTS groups;
  DROP TABLE IF EXISTS sightings;
  DROP TABLE IF EXISTS points;

-- Primate social groups
CREATE TABLE groups (
    groupid         TEXT NOT NULL PRIMARY KEY,
    scientific_name TEXT,
    common_name     TEXT
);

-- Individual primates
CREATE TABLE individuals (
    individual_id   TEXT PRIMARY KEY,
    groupid         TEXT NOT NULL REFERENCES groups(groupid),
    age             TEXT,
    sex             TEXT,
    date_named      TEXT
);

-- Observer sightings of primate groups
CREATE TABLE sightings (
    sighting_id         TEXT NOT NULL PRIMARY KEY,
    observersample_id   TEXT NOT NULL REFERENCES observersamples(observersample_id),
    groupid             TEXT NOT NULL REFERENCES groups(groupid),
    date_seen           TEXT NOT NULL,
    time_seen           TEXT NOT NULL,
    follow_data_included  BOOLEAN NOT NULL DEFAULT FALSE,
    time_left_lost     TEXT
);

-- Daily observer samples
    CREATE TABLE observersamples (
    observersample_id   TEXT NOT NULL PRIMARY KEY,
    observer_name       TEXT NOT NULL,
    observersample_date TEXT NOT NULL
);

-- GPS Points
CREATE TABLE points (
    observersample_id   TEXT NOT NULL REFERENCES observersamples(observersample_id),
    point_date           TEXT NOT NULL,
    point_time           TEXT NOT NULL,
    lat                REAL NOT NULL,
    lon                REAL NOT NULL,
    utm_x              REAL NOT NULL,
    utm_y              REAL NOT NULL
)