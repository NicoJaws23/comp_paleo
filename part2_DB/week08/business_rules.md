# Business Rules
## Nico Jaworski

## Rule Inventory
| RULE                                                                                              | Enforceable in SQL? | Constraint Type | SQL expression or note                                                     |
|---------------------------------------------------------------------------------------------------|---------------------|-----------------|----------------------------------------------------------------------------|
| primate_ids must be at least 2 characters to at least note age-sex classification                  | Yes                 | CHECK           | CHECK (length(trim(primate_id)) >= 2)                       |
| Each observer must have a unique observer_id                                                      | Yes                 | NOT NULL        | observer_id INTEGER NOT NULL                                               |
| Each observer must have their last name entered into the observer_last_name field                 | Yes                 | NOT NULL        | observer_last_name TEXT NOT NULL                                           |
| Observer sample IDs must be no longer than 7 characters                                           | Yes                 | CHECK           | check (length(trim(observer_sample_id)) = 7)                                |
| Observer sample IDs, avistaje IDs, and focal sample IDs must all be unique in their parent tables | Yes                 | UNIQUE          | UNIQUE (observer_sample_id), UNIQUE (avitaje_id), UNIQUE (focal_sample_id) |
| The end time of an avistaje follow cannot be earlier than the start time of the follow            | Yes                 | CHECK           | CHECK (time_left_lost > time_seen)                                         |
| The duration of an avistaje or focal follow cannot go over 24 hours                                            | Yes                 | TIME Data type contraints          | Comparing the start and end times prevents the duration from being 24 hours or longer since the largest value can only be 23:59:59                                              |
| lat and lon data should both be less than 0 given the location of the field site                                 | Yes                 | NOT NULL        | observer_sample_id TEXT NOT NULL                                           |

## Cross-Field Constraints

-- time_left_lost must be later in the day (greater value because 24 hour format) than
-- time_seen in avistaje table
CHECK (time_left_lost > time_seen)

-- time_left_lost cannot be NULL if follow_data_included is TRUE
CHECK (NOT (time_left_lost IS NULL AND follow_data_included = TRUE))