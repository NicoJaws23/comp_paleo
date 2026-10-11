-- contraints_tests.sql
-- Nico Jaworski
-- 2026-11-10

-- Background setup to run tests --
PRAGMA foreign_keys = ON;
INSERT INTO groups (group_id, scientific_name, common_name)
VALUES ('Lagothrix G', 'Lagothrix lagotricha', 'Lowland woolly monkey');

INSERT INTO observers (observer_name, observer_first_name, observer_last_name)
VALUES ('Nico Jaworski', 'Nico', 'Jaworski');

-- NOT NULL on group_id in groups table --

-- SHOULD SUCCEED
INSERT INTO groups (group_id, scientific_name, common_name)
VALUES ('Ateles G', 'Ateles belzebuth', 'White-bellied spider monkey');

-- SHOULD FAIL: group_id is NOT NULL
-- Expected error: NOT NULL constraint failed: groups.group_id
INSERT INTO groups (group_id, scientific_name, common_name)
VALUES (NULL, 'Ateles belzebuth', 'White-bellied spider monkey');

-- CHECK on observer_sample_id in observer_samples table --

-- SHOULD SUCCEED
INSERT INTO observer_samples (observer_sample_id, observer_name, sample_date)
VALUES ('OS71674', 'Nico Jaworski', '2026-11-10');

-- SHOULD FAIL: observer_sample_id must be exactly 7 characters long
-- Expected error: CHECK constraint failed: length(trim(observer_sample_id)) = 7
INSERT INTO observer_samples (observer_sample_id, observer_name, sample_date)
VALUES ('OS7167', 'Nico Jaworski', '2026-11-10');

-- CHECK on time_left_lost >= time_seen in avistajes table --

-- SHOULD SUCCEED
INSERT INTO avistajes (avistaje_id, observer_sample_id, group_id, time_seen, follow_data_included, time_left_lost)
VALUES ('AV23456', 'OS71674', 'Lagothrix G', '10:00:00', TRUE, '10:30:00');

-- SHOULD FAIL: time_left_lost must be greater than or equal to time_seen
-- Expected error: CHECK constraint failed: time_left_lost >= time_seen OR time_left_lost IS NULL
INSERT INTO avistajes (avistaje_id, observer_sample_id, group_id, time_seen, follow_data_included, time_left_lost)
VALUES ('AV23457', 'OS71674', 'Lagothrix G', '10:00:00', TRUE, '09:30:00');

-- UNIQUE on observer_name in observers table --

-- SHOULD SUCCEED
INSERT INTO observers (observer_name, observer_first_name, observer_last_name)
VALUES ('Jane Doe', 'Jane', 'Doe');

-- SHOULD FAIL: 'Nico Jaworski' already exists
-- Expected error: UNIQUE constraint failed: observers.observer_name
INSERT INTO observers (observer_name, observer_first_name, observer_last_name)
VALUES ('Nico Jaworski', 'Nico', 'Jaworski');

-- ON DELETE RESTRICT (observers -> observer_samples) --

-- Setup: a throwaway observer with one observer sample
INSERT INTO observers (observer_name, observer_first_name, observer_last_name)
VALUES ('Temp Observer', 'Temp', 'Observer');
INSERT INTO observer_samples (observer_sample_id, observer_name, sample_date)
VALUES ('OS12345', 'Temp Observer', '2026-11-10');

-- SHOULD FAIL: observer still has observer samples
-- Expected error: FOREIGN KEY constraint failed
DELETE FROM observers WHERE observer_name = 'Temp Observer';

-- SHOULD SUCCEED: delete the child first, then the parent
DELETE FROM observer_samples WHERE observer_sample_id = 'OS12345';
DELETE FROM observers WHERE observer_name = 'Temp Observer';

-- ON DELETE SET NULL (groups -> primate_ids) --

-- Setup: a throwaway group with one primate
INSERT INTO groups (group_id) VALUES ('Temp Group');
INSERT INTO primate_ids (primate_id, group_id, sex, age_class)
VALUES ('Gata', 'Temp Group', 'Male', 'Adult');

-- SHOULD SUCCEED: deleting the group nulls the primate's group_id
DELETE FROM groups WHERE group_id = 'Temp Group';

-- Expected result: 1
SELECT group_id IS NULL FROM primate_ids WHERE primate_id = 'Gata';

