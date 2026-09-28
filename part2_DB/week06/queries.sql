-- queries.sql
-- OTB Fossil Database Queries
-- Week 6 Assignment

-- ── Query 1 ───────────────────────────────────────────────────────────────────
-- Question: How many fossil specimens are in the database?
-- Write a SELECT query that returns the total row count of the fossils table.
\echo Query 1: How many fossil specimens are in the database?
SELECT COUNT(*) FROM fossils; -- SELECT used COUNT(*) to return the total number of fossils in the fossils table based on the number of rows.

-- ── Query 2 ───────────────────────────────────────────────────────────────────
-- Question: Which specimens were discovered by Kamoya Kimeu?
-- Write a SELECT query returning catalog_number, preparations, and year
-- for all fossils where discovered_by contains 'Kimeu',
-- ordered by year ascending.
\echo Query 2: Which specimens were discovered by Kamoya Kimeu?
SELECT catalog_number, preparations, year -- Specifies that catalog_number, preparations, and year should be returned.
    FROM fossils -- Specifies we are looking in the fossils table.
    WHERE discovered_by LIKE '%Kimeu%' -- Searchers the discovered_by column for rows that contain Kimeu. The % wildcards allow for flexibility when searching, like if there is more than just Kimeu in the cell.
    ORDER BY year ASC; -- Orders results by year in ascending order.

-- ── Query 3 ───────────────────────────────────────────────────────────────────
-- Question: How many specimens come from each formation?
-- Write a SELECT query that joins fossils to localities, groups by formation,
-- and returns the formation name and specimen count, ordered by count descending.
\echo Query 3: How many specimens come from each formation?
SELECT l.formation, COUNT(*) AS specimen_count -- Specifies that the name of the formation and the count of specimens in each formation should be returned.
    FROM fossils f -- Specifies the fossils table and gives it an aslias of f.
    JOIN localities l ON f.locality_id = l.locality_id -- Give the localities table an alias of l before joinging the table by the locality_id foreign key.
    GROUP BY l.formation -- Groups COUNT(*) results by formation type
    ORDER BY specimen_count DESC; -- Orders results in descending order.

-- ── Query 4 ───────────────────────────────────────────────────────────────────
-- Question: Which specimens are older than 3 million years?
-- Write a SELECT query returning catalog_number, scientific_name,
-- earliest_chronometric_age, and formation for fossils where
-- earliest_chronometric_age > 3.0, ordered by age descending.
-- This requires joining fossils to both taxa and localities.
\echo Query 4: Which specimens are older than 3 million years?
SELECT f.catalog_number, t.scientific_name, f.earliest_chronometric_age, l.formation -- Specifies the catalog_number, scientific_nam, earliest_chronometric_age, and formation will be returned.
    FROM fossils f -- Gives fossils alias of f.
    JOIN taxa t on f.taxon_id = t.taxon_id -- Gives taxa the alias of t and then joins fossils and taxa by the taxon_id foreign key.
    JOIN localities l on f.locality_id = l.locality_id -- Gives localities the alias of l and then joins the fossils/taxa joined table with localities by the locality_id foreign key.
    WHERE f.earliest_chronometric_age > 3.0 -- Filters to only return foossils older than 3 million years.
    ORDER BY f.earliest_chronometric_age DESC; -- Prints the reuslts in descending order based on earliest_chronometric_age.

-- ── Query 5 ───────────────────────────────────────────────────────────────────
-- Question: Which taxon has the most specimens, and what anatomical
-- elements are most commonly preserved for that taxon?
-- Write two queries:
-- (a) Find the scientific_name with the highest specimen count.
-- (b) For that taxon, show the distribution of preparations values
--     with counts, ordered by count descending.
\echo Query 5: Which taxon has the most specimens, and what anatomical elements are most commonly preserved for that taxon?

SELECT t.scientific_name, COUNT(*) AS specimen_count -- Specifies that the scientific_name and the count of specimens for each taxon should be returned.
    FROM fossils f -- Assigns the fossils table an alias of f.
    JOIN taxa t ON f.taxon_id = t.taxon_id -- Assigns the taxa table an alias of t and joins fossils and taxa by the taxon_id foreign key.
    GROUP BY t.scientific_name -- Groups the results of COUNT(*) by scientific_name.
    ORDER BY specimen_count DESC -- Orders the results in descending order based on specimen_count.
    LIMIT 1 -- Limits the list to just 1, which is the taxon with the highest specimen count. Below, \gset top_ saves the result to a variable called top_scientific_name and top_specimen_count for use in the next query.
    \gset top_ 

-- The line below prints the name of the top taxon and the number of specimens it has.
\echo Top taxon: :top_scientific_name (:top_specimen_count specimens)

SELECT f.preparations, COUNT(*) AS preparation_count -- Specifies the we are looking in the preparations column and then counts the number of each preparation
    FROM fossils f -- Gives fossils an alias of f.
    JOIN taxa t ON f.taxon_id = t.taxon_id -- Assigns taxa the alias t and joins it to fossils by the taxon_id foreign key.
    WHERE t.scientific_name = :'top_scientific_name' -- Filters joined table for where the scientific_name is equal to the top_scientific_name variable from the previous query.
    GROUP BY f.preparations -- Groups preparations of the top taxon based on the type of preparation (tooth, cranium, etc.)
    ORDER BY preparation_count DESC; -- Orders the couunts of each preparation type in descending order.