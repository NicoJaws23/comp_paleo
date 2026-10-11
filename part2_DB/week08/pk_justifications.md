# Primary Key Justifications
## Nico Jaworski


### Table: groups

Key field(s): group_id
Key type: Natural

Justification:
For group_id I chose a natural key. Each social group of primates has previously been designated based on its genus and then a letter differentiating it from groups of the same species (ex: Lagothrix G, Lagothrix D). This natural key would not change, however the associated data from in the species_name field could should future taxanomic revisions occur.

### Table: primate ids

Key field(s): primate_id (PK), group_id (FK)
Key type: Natural

Justification:
primate_id is the primary natural key for this table because it is (overall) unique to individual known primates. There are primate ids which are just the age-sex class combination (AM is adult male, JF3 is juvenile female 3) held in this table. This is not a composite key situation as the key is not based on a combination of values from other columns, primate_ids are entered as new primates are identified. The values in primate_id should not change over time, however the age classification or group each primate belongs to could theoretically change, but this should not cause issues because the linking key is not changing.

### Table: observers

Key field(s): observer_id (PK)
Key type: Surrogate

Justification:
observer_id is a surrogate primary key which assiigns a unqiue integrer to each observer. I made this choice in case observer names should change in the future (like changing last names for marriage). That way, any data associated with that same observer is still tied to them, even if their name changes.

### Table: observer sample

Key field(s): observer_sample_id (PK), observer_id (FK), observer_name (FK)
Key type: Natural

Justification:
observer_sample_id is a natural primary key entered by indiviual observers each day. observer_sample_ids will not change and are unique to date the observer is in the field. This key is not a surrogate key becuase each observer sample id has a prefix of OS, so it is more than just an integer.

### Table: avistajes

Key field(s): avistaje_id (PK), observer_sample_id (FK), group_id (FK)
Key type: Natural

Justification:
avistaje_id is a natural primary key entered by observers whenever they see a primate group, no matter the species. It is a unique value per each sighting, however there can be multiple sightings per day, so one observer sample id may have many avistaje ids associated with it. Similar to observer_sample_id, this is not a surrogate key becuase of each id has an AV prefix.

### Table: focal sample

Key field(s): focal_sample_id (PK), avistaje_id (FK), primate_id (FK)
Key type: Natural

Justification:
focal_sample_id is a natural primary key which observers manually enters on their data collection devices (iPods) whenever they are conducting a focal sample on an individual primate. This is a unique number for each individual focal sample and the data held withing, following a similar convention to observer_sample_id and avistaje_id. FS12345 is an example, this record would be associated with a particular avistaje_id, representing the time the whole group was followed. So one avistaje may have many focal samples within it. The number assigned to a focal sample will not change, but the data within can. So if an observer accidently marks an adult male as an adult female, the age-sex id can be changed without changing the entire focal sample.

### Table: focal data

Key field(s): focal_data_id (PK), focal_sample_id (FK), partner (FK), nearest_neighbor_id (FK)
Key type: Surrogate

Justification:
Each focal sample has individual focal data records held within it. So I need a way to individuall ID each of these records in case changes need to be made to one or more of them. focal_data_id will thus be a surrogate primary key which assigns an integer value to each record starting at 0 and going up from there.

### Table: gps points

Key field(s): gps_point_id (PK), observer_sample_id (FK)
Key type: Surrogate

Justification:
Each individual gps point needs a unique identifier to track it down in case an error is found. For example, at times the satelites get wonky and suddenly record our posistion as a few kilometers away from where we actually are. We can find this pretty easily with visual inspection, so giving each point a unqiue ID will make it easy to pin down where the error is in the data set and fix it. gps_point_id is a surrogate primary key because there is not need for observers to individually name each point (which is about 2000+ points for a 12 hour follow day), so having sql give each point an id is much smoother.