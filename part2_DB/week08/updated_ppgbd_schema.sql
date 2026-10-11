-- updated_ppgbd_schema.sql
-- Proyecto Primates Geographic and Behavioral Database Schema
-- Nico Jaworski
-- 2026-11-10

DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS primate_ids;
DROP TABLE IF EXISTS observers;
DROP TABLE IF EXISTS observer_samples;
DROP TABLE IF EXISTS avistajes;
DROP TABLE IF EXISTS focal_samples;
DROP TABLE IF EXISTS focal_data;
DROP TABLE IF EXISTS gps_points;

PRAGMA foreign_keys = ON;

-- group IDs
-- Table holds the unqiue IDs and species information for each primate group
CREATE TABLE groups (
    -- Primary Key
    group_id TEXT PRIMARY KEY NOT NULL 
    CHECK (group_id = trim(group_id) AND length(group_id) > 0),

    -- Optional fields
    scientific_name TEXT, -- NULL permitted because there is a general Unknown group option for all species
    common_name TEXT, -- NULL permitted because of unknown group option

    -- Unique Constraints
    UNIQUE (group_id)
);

-- prmimate IDs
-- Tables holds both known names (ex: Gata, Chuchaki) and unknown individuals (ex: AM, AF, JF2) in all primate groups
CREATE TABLE primate_ids (
    -- Primary Key
    primate_id TEXT PRIMARY KEY NOT NULL
    CHECK (length(trim(primate_id)) >= 2),

    -- Foreign Key
    group_id TEXT -- NULL permitted here because some IDs are not associated with a specific group. For example, adult males (AM) can be found in all groups
    REFERENCES groups(group_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE, 

    -- Optional fields
    sex TEXT NOT NULL,
    age_class TEXT NOT NULL,

    -- Unique Constraints
    UNIQUE (primate_id)
);

-- observer information
-- Table holds information about the observers who collect data in the field
CREATE TABLE observers (
    -- Primary Key
    observer_id INTEGER PRIMARY KEY NOT NULL,

    -- Required fields
    observer_name TEXT NOT NULL,
    observer_first_name TEXT NOT NULL,
    observer_last_name TEXT NOT NULL
    CHECK (length(trim(observer_last_name)) >= 2),
    
    -- Optional fields
    primary_contact TEXT, -- NULL permitted here in case observer does not have a primary contact method or does not want to share it
    institution TEXT, -- NULL permitted here in case observer is not a member of specific institution

    -- Unique Constraints
    UNIQUE (observer_name)
);

-- observer samples
-- Holds information of an observers daily observer sample (what they did that day while out, the date they were out, etc)
CREATE TABLE observer_samples (
    -- Primary Key
    observer_sample_id TEXT PRIMARY KEY NOT NULL
    CHECK (length(trim(observer_sample_id)) = 7),

    -- Foreign Keys
    observer_name TEXT NOT NULL 
    REFERENCES observers(observer_name)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

    -- Required fields
    sample_date DATE NOT NULL,

    -- Optional fields
    gps_used TEXT, -- NULL permitted here becasue not every observer sample is associated with GPS data, for example if I stayed in camp that day I would not have used a GPS
    notes TEXT, -- NULL permitted here because not every observer sample will have notes

    -- Unique Constraints
    UNIQUE (observer_sample_id)
);


-- avistajes
-- Holds information on specific sightings of primate groups, including the time of the sighting and whether or not follow data was collected
CREATE TABLE avistajes (
    -- Primary Key
    avistaje_id TEXT PRIMARY KEY NOT NULL
    CHECK (length(trim(avistaje_id)) = 7),

    -- Foreign Keys
    observer_sample_id TEXT NOT NULL
        REFERENCES observer_samples(observer_sample_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    group_id TEXT
        REFERENCES groups(group_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    -- Required fields
    time_seen TIME NOT NULL,
    follow_data_included BOOLEAN NOT NULL DEFAULT FALSE,

    -- Optional fields
    time_left_lost TIME, -- NULL permitted because not every avistaje will have a value if follow data is not included
    duration TEXT GENERATED ALWAYS AS (
        CASE WHEN time_left_lost IS NOT NULL
        THEN time(strftime('%s', time_left_lost) - strftime('%s', time_seen), 'unixepoch')
        END
    ) VIRTUAL, -- NULL when there is no time_left_lost
    notes TEXT, -- NULL permitted because not every avistaje will have notes

    -- Unique Constraints
    UNIQUE (avistaje_id),

    -- Cross-field business rules
    CHECK (time_left_lost >= time_seen OR time_left_lost IS NULL),
    CHECK (NOT (time_left_lost IS NULL AND follow_data_included = TRUE))
);

-- focal samples
-- Tables holds data on who a focal sample was on, the start and end times of the focal, and any notes
CREATE TABLE focal_samples (
    -- Primary Key
    focal_sample_id TEXT PRIMARY KEY NOT NULL
    CHECK (length(trim(focal_sample_id)) = 7),

    -- Foreign Keys
    avistaje_id TEXT NOT NULL
        REFERENCES avistajes(avistaje_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    primate_id TEXT -- NULL permitted here in case observer cannot make out ID of focal or forgets to input it
        REFERENCES primate_ids(primate_id)
        ON DELETE SET NULL
        ON UPDATE NO ACTION,

    -- Required fields
    time_start TIME NOT NULL,
    time_end TIME NOT NULL,

    -- Optional fields
    notes TEXT, -- NULL permitted because not every focal sample will have notes

    -- Unique Constraints
    UNIQUE (focal_sample_id),

    -- Cross-field business rules
    CHECK (time_end >= time_start)
);

-- focal data
-- Holds individual behavioral records associated with a specific focal sample
CREATE TABLE focal_data (
    -- Primary Key
    focal_data_id INTEGER PRIMARY KEY NOT NULL,

    -- Foreign Keys
    focal_sample_id TEXT NOT NULL
        REFERENCES focal_samples(focal_sample_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    social_partner TEXT -- NULL permitted here in case observer cannot make out ID of partner or if partner does not exist
        REFERENCES primate_ids(primate_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    nearest_neighbor TEXT -- NULL permitted here in case observer cannot make out ID of nearest neighbor or if nearest neighbor does not exist
        REFERENCES primate_ids(primate_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    -- Required fields
    behavior TEXT NOT NULL,
    behavior_start_time TIME NOT NULL,

    -- Optional fields
    behavior_end_time TIME, -- NULL permitted here because not every behavior has a duration (eg: a foraging bout will, but vocalizations may not)
    partner_behavior TEXT, -- NULL permitted here because there is not always a partner
    social_time_begin TIME, -- NULL permitted because not every record will be a partner/social behavior activity
    social_time_end TIME, -- NULL permitted because not every record will be a partner/social behavior activity
    nearest_neighbor_distance TEXT, -- NULL permitted because not every record will have a nearest neighbor
    nearest_neighbor_behavior TEXT, -- NULL permitted because not every record will have a nearest neighbor
    proximity TEXT, -- NULL permitted because not every record will have individuals within proximity
    notes TEXT, -- NULL permitted because not every focal data record will have notes

    -- Unique Constraints
    UNIQUE (focal_data_id),

    -- Cross-field business rules
    CHECK (behavior_end_time >= behavior_start_time OR behavior_end_time IS NULL),
    CHECK (social_time_end >= social_time_begin OR social_time_end IS NULL)
);

-- gps points
-- Table holds GPS points associated with observer samples, including the time of the point and the coordinates
CREATE TABLE gps_points (
    -- Primary Key
    gps_point_id INTEGER PRIMARY KEY NOT NULL,

    -- Foreign Keys
    observer_sample_id TEXT NOT NULL
        REFERENCES observer_samples(observer_sample_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Required fields
    point_date DATE NOT NULL,
    point_time TIME NOT NULL,
    lat REAL NOT NULL
    CHECK (lat <= 0),
    lon REAL NOT NULL
    CHECK (lon <= 0),
    utm_x REAL NOT NULL,
    utm_y REAL NOT NULL,


    -- Unique Constraints
    UNIQUE (gps_point_id)
);