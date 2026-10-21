-- ppgbd_sqlite_schema_simple.sql
-- Proyecto Primates Geographic and Behavioral Database Schema
-- Nico Jaworski
-- 2026-10-21


DROP TABLE IF EXISTS focal_samples;
DROP TABLE IF EXISTS avistajes;
DROP TABLE IF EXISTS observer_samples;

-- observer sample data, first thing entered each day
CREATE TABLE observer_samples (
    Obs_Sample_ID        TEXT PRIMARY KEY NOT NULL
        CHECK (length(trim(Obs_Sample_ID)) = 7),
    Observer             TEXT,
    Obs_Date             DATE,
    Time_Record_Created  TIMESTAMP,
    Comments             TEXT,
    GPS_Used             TEXT
);

-- avistaje data, any sightings of primate groups
CREATE TABLE avistajes (
    Avistaje_ID          TEXT PRIMARY KEY NOT NULL
        CHECK (length(trim(Avistaje_ID)) = 7),
    Obs_Sample_ID        TEXT NOT NULL
        REFERENCES observer_samples(Obs_Sample_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    Taxon                TEXT,
    Group_Name           TEXT,
    Time_Enc             TIME,
    Beh_When_Enc         TEXT,
    Follow_Data_Included BOOLEAN DEFAULT FALSE,
    Time_Left_Lost       TIME,
    How_Ended            TEXT,
    Avistaje_Notes       TEXT,
    Voc_Contact          BOOLEAN DEFAULT FALSE,
    Voc_Distance         TEXT,
    Other_Observers_Present TEXT

);

CREATE TABLE focal_samples (
    Focal_Sample_ID      TEXT PRIMARY KEY NOT NULL
        CHECK (length(trim(Focal_Sample_ID)) = 7),
    Avistaje_ID          TEXT NOT NULL
        REFERENCES avistajes(Avistaje_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    Focal_Animal         TEXT,
    Focal_Age_Sex_Class  TEXT,
    Time_Start           TIME,
    Time_End             TIME,
    Comments             TEXT

);