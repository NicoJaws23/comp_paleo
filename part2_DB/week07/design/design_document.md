## Proyecto Primates Geographic and Behavioral Database (PPGBD)

The purpose of the Proyecto Primates Geographic and Behavioral Database is to store and maintain primate behavioral data to seamlessly evaluate primate ranging patterns and the distribution of 
behavioral patterns across the landscape.

## PPGBD Objectives
1: Link observer data to gps data to map observations
SELECT o.date, o.time, o.data 
FROM observarions  o
JOIN gpsData g ON o.osid = g.osid

2: Calcuulate occurances of different behaviors per social group
SELECT o.behavior, o.groupid, count(*) AS n_occurences
FROM observations o
GROUP BY o.groupid, o.behavior
ORDER BY o.groupid, n_occurences DESC;

3: Select all travel points for each group
SELECT s.groupid
FROM sightings s
JOIN gpsData g ON s.osid = g.osid
GROUP BY s.osid;


4: Record number of observations made by each observer
SELECT observer, count(*) AS n_observations
FROM observations o
GROUP BY observer
ORDER BY n_observations;

5: Calculate number of observations of each species of primate
SELECT g.species, COUNT(*) AS observation_count
FROM observations AS o
JOIN groups AS g ON o.groupid = g.groupid
GROUP BY g.species
ORDER BY observation_count DESC;

## PPGBD Entities
| Entity | Justification | Example Attributes |
| :------: | :-------------: | :------------------: |
| Groups  | Each social group has its own identity, species name, common name, and rough demographics | groupid, species_name, common_name |
| Individuals | Known individuals each have their own name and unique age-sex demographics and group they belong to | name, age, sex, groupid, date_named |
| Sightings | Whenever one or more primate are seen we record information on the context of when and where we saw then | sighting_id, group_id, date, time, follow_data_included, time_left_lost |
| Points | Observers record gps points to map where the group went and this needs to be linked to observational records | observation_id, date, time, lat, lon, utm_x, utm_y |
| Observer Samples | Each day we need a record of what the observer was doing and to also link back to their gps track | observersample_id, date |

## Field Specifications

### Groups Entity
| Field Name | Data Type | Required | Default | Notes |
| :--------: | :-------: | :------: | :-----: | :---: |
| groupid | TEXT | YES(PK) | | Identifies specific groups to relate to other tables, ex Lagothrix G |
| species_name | TEXT | NO | | Notes the scientific name of the species in the group |
| common_name | TEXT | NO | | Indicates the common name of the species in the group |

### Individuals
| Field Name | Data Type | Required | Default | Notes |
| :--------: | :-------: | :------: | :-----: | :---: |
| individual_id | TEXT | YES(PK) | | Name of specific name individual, required to reference in focal sample data |
| age | TEXT | NO | | Qualitative value of age, ex juvenile, adult, etc |
| sex | TEXT | NO | | Sex classification of known individual, male or female | 
| groupid | TEXT | YES(FK) | | Group individual belongs too, required to communicate with group entity |
| date_named | DATE | NO | | Date when individual was first identified and named in YYYY-MM-DD format | 

### Sightings
| Field Name | Data Type | Required | Default | Notes |
| :--------: | :-------: | :------: | :-----: | :---: |
| observersample_id | TEXT | YES(FK) | | Unique identifier for that days oberser data, such as gps used |
| sighting_id | TEXT | YES(PK) | | Unique identifier per sighting, ex AV12345 |
| group_id | TEXT | YES(FK) | | Identity of group seen | 
| date | DATE | YES | | Date of sighting, needed to reference geospatial data |
| time | TIME | YES | | Start time of observation, needed to reference geospatial data
| follow_data_included | LOGICAL | YES | FALSE | Was the group followed, if so it needs to be recorded |
| time_left_lost | TIME | NO | | If group was followed, need to know end time |

### Points
| Field Name | Data Type | Required | Default | Notes |
| :--------: | :-------: | :------: | :-----: | :---: |
| obsersample_id | TEXT | YES(FK) | | Used to distinguish who's data this is |
| date | DATE | YES | | Date each point was from, need for refrenceing to sightings |
| time | TIME | YES | | Time of each point, 20-second intervals | 
| lat | NUMERIC | YES | | Latitude data |
| lon | NUMERIC | YES| | Longitude data |
| utm_x | NUMERIC | YES | | easting data for UTM Zone 18S |
| utm_y | NUMERIC | YES | | northing data for UTM Zome 18S |

### Observer Samples
| Field Name | Data Type | Required | Default | Notes |
| :--------: | :-------: | :------: | :-----: | :---: |
| observersample_id | TEXT | YES(PK) | | Unique identifer of that day, ex OS12345 |
| observer_name | TEXT | YES(FK) | | Name of specific observer | 
| date | DATE | YES | | Date of observer being active |

## Relationships and Keys

| Relationship | Cardinality | Implementation |
| One group --> many individuals | 1:Many | groups.group_id --> individuals.group_id |
| One group --> many sightings | 1:Many | group.group_id --> sightings.group_id |
| One observer sample --> many points | 1:Many | observersamples.observersample.id --> points.observersample.id |
| One observer --> many observer samples | 1:Many | observers.observer_name --> observersamples.observer_name