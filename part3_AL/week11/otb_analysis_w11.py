# %% [markdown]
# # Week 11 Assignment: Data Loading, Cleaning, and Joining

# %% load in tool packages and DSN
from sqlalchemy import engine
import json
import os

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

from config import DSN

engine = create_engine(DSN)

# %% Part 1
# %% Loading and viewing JSON with the standard library
with open('ecv_otb_subset.json') as f:
    ecv_raw = json.load(f)

print("Data Source:", ecv_raw['source'])
print("Region Field:", ecv_raw['region'])
print("Number of Specimens:", len(ecv_raw['specimens']))

# %% Converting Specimens List from JSON file to DataFrame
ecv_otb = pd.json_normalize(ecv_raw['specimens'])

print("Data Types:", ecv_otb.dtypes)
print("Data Shape:", ecv_otb.shape)

# %% [markdown]
# # A
# null in JSON becomes NaN, None, or NaT depending on the original data
# type in the JSON file. If a JSON column dtype is numeric it becomes NaN
# and the column in pandas becomes a float64 dtype. Is the JSON column
# type is text or Boolean it becomes None and an object dtype. Finally,
# if the JSON column type is dates or time it becomes NaT and the dtype is
# datetime64[ns]
# # B
# While some values in ecv_median_cm3 are whole numbers, they still contain a decimal place, and some of these values
# have values that are not 0. For example, specimen 7 has an ecv_median_cm3 value of 756.2, so the entire column
# needs to be float64.
# # C
# One senario where I would use dtype to overide the default inference may be
# if I need to convert a column to match the data type from another table for
# a join or if I was trying to do some basic arithmetic and needed to ensure
# that the data type was numeric for example. 
# %% Load OTB fossil data from PostrgreSQL and compare with csv version
df = pd.read_sql("""
    SELECT f.*,
           l.place, l.subregion, l.country, l.state_province, l.formation, l.member,
           t.scientific_name, t.identification_qualifier
    FROM fossils f
    LEFT JOIN localities l ON f.locality_id = l.locality_id
    LEFT JOIN taxa t       ON f.taxon_id    = t.taxon_id
""", engine)

df.to_csv('otb_fossils.csv', index=False)

df_csv = pd.read_csv('otb_fossils.csv')

print(set(df.columns) == set(df_csv.columns))
print("PostgreSQL Data Types:", df.dtypes)
print("CSV Version Data Types:", df_csv.dtypes)
# %% [markdown]
# # Data Type Differences
# When I compared the psql data types with a csv version I did not find any differences in the data types.
# Could this be because of how I generate the table? Or an update to the code?

# %% Part 2
# %% 1: Checking for null and adding grade and time_bin columns
ecv_full = pd.read_csv('ecv_by_specimen.csv')
print("Null Values Per Columns:", ecv_full.isnull().sum())

grade_labels = {
    'archaic': 'Archaic australopith',
    'mega':    'Robust australopith / Paranthropus',
    'trans':   'Transitional (H. habilis)',
    'pre.mod': 'Pre-modern Homo'
}
ecv_full['grade_label'] = ecv_full['grade'].map(grade_labels)

bins   = [0.0, 1.0, 2.0, 2.6, 3.5]
labels = ['Late Pleistocene', 'Early Pleistocene', 'Plio-Pleistocene', 'Pliocene']

ecv_full['time_bin'] = pd.cut(ecv_full['age_mid_Ma'],
                               bins=bins, labels=labels)

print(ecv_full['grade_label'].value_counts())                               
print(ecv_full['time_bin'].value_counts())

# %% 2: Filter for Paranthropus and Homo
genus = {
    'Au. afarensis': 'Australopithecus',
    'Au. africanus': 'Australopithecus',
    'Au. garhi': 'Australopithecus',
    'Au. sediba': 'Australopithecus',
    'H. erectus': 'Homo',
    'H. habilis': 'Homo',
    'H. heidelbergensis': 'Homo',
    'P. aethiopicus': 'Paranthropus',
    'P. boisei': 'Paranthropus',
    'P. robustus': 'Paranthropus'
}
ecv_full['genus'] = ecv_full['taxon'].map(genus)

ecv_hominin = ecv_full[(ecv_full['genus'] == 'Homo') | (ecv_full['genus'] == 'Paranthropus')]
print("Dataset Shape:", ecv_hominin.shape)
print('Taxa:', sorted(ecv_hominin['taxon'].unique()))
# %% [markdown]
# # Why Exclude Australopithecus
# It might be good to exclude Australopithecus because Au. were more frequently found in Ethiopia. 
# The Turkana Basin lies mostly in Kenya, where Homo and Paranthropus are more frequently found and
# believed to have thrived.

# %% 3: Analyze ecv_hominin

ecv_by_bin = (
    ecv_hominin
    .groupby('time_bin', observed=True)['ecv_median_cm3']
    .agg(mean='mean', min='min', max='max', count='count')
    .round(1)
)
print(ecv_by_bin)

# Add grade
ecv_by_bin_grade = (
    ecv_hominin
    .groupby(['time_bin', 'grade'], observed=True)['ecv_median_cm3']
    .agg(mean='mean', min='min', max='max', count='count')
    .round(1)
)
print(ecv_by_bin_grade)

# %% [markdown]
# # Change in ECV Through Time
# Over time, ECV increased from the Plio-Pleistocene to the present. This appears to be consistent across
# grades, at least the grades of mega and pre.mod

# %% Part 3: Joining Data

# %% 1 - Taxon Name Comparison and Fixing
fossils = pd.read_sql(
    "SELECT f.*, t.scientific_name FROM fossils f JOIN taxa t USING (taxon_id)",
    engine
)

# Compare taxon names
print("OTB taxa:", sorted(fossils['scientific_name'].unique()))
print("ECV taxa:", sorted(ecv_full['taxon'].unique()))

# Fixing Names
taxon_map = {
 'Australopithecus Dart, 1925': 'Australopithecus',
 'Australopithecus anamensis Leakey et al., 1995': 'Au. anamensis',
 'Hominini': 'Hominini',
 'Homo Linnaeus, 1758': 'Homo',
 'Homo erectus (Dubois, 1892)': 'H. erectus',
 'Homo habilis Leakey, Tobias & Napier, 1964': 'H. habilis',
 'Kenyanthropus platyops Leakey et al., 2001': 'K. platyops',
 'Paranthropus Broom, 1938': 'Paranthropus',
 'Paranthropus aethiopicus (Arambourg & Coppens, 1967)': 'P. aethiopicus',
 'Paranthropus boisei (Leakey, 1959)': 'P. boisei'
}

# Create a taxon_name row in the fossils.df
fossils['taxon_name']=fossils['scientific_name'].map(taxon_map)
print(fossils['taxon_name'])

# Compare taxon names gain
print("OTB taxa:", sorted(fossils['taxon_name'].unique()))
print("ECV taxa:", sorted(ecv_full['taxon'].unique()))

# %% [markdown]
# # Name Changes
# The only change I had to make was abbreviating the genus names of specimens in the OTB fossils data.
# In both OTB and ECV, species names were the same for matching species (ex: H. habilis is H. habilis in both).ModuleNotFoundError

# %% 2 - Joining Tables
ecv_by_taxon = (
    ecv_full
    .groupby('taxon')['ecv_median_cm3']
    .agg(ecv_mean='mean', ecv_median='median',
         ecv_min='min', ecv_max='max', ecv_n='count')
    .reset_index()
)
print(ecv_by_taxon)

fossils_ecv = pd.merge(
    fossils,
    ecv_by_taxon,
    left_on='taxon_name', right_on='taxon',
    how='left'
)
print(fossils_ecv['ecv_mean'].isnull().sum())   # taxa with no ECV data

print("Original Dataframe:", fossils.shape)
print("Joined Dataframe:", fossils_ecv.shape)
# %% [markdown]
# # Why The Same Value
# Since we did a left join to fossils, all rows from fossils are retained, meaning the new table
# will have the same number of rows as fossils did before the join.
print("Data Sample:", fossils_ecv[['catalog_number', 'taxon_name', 'ecv_mean']].head(10))
print("Count of Null Data:", fossils_ecv['ecv_mean'].isnull().sum())
print("Taxa with no ECV:\n",
      fossils_ecv.loc[fossils_ecv['ecv_mean'].isnull(), 'taxon_name'].value_counts())

# %% 3 - Specimens Join
# # Specimen-level join — only works where catalog_number == ECV specimen ID
specimen_join = pd.merge(
    fossils,
    ecv_full[['ID', 'ecv_median_cm3', 'age_lo_Ma', 'age_hi_Ma', 'n_estimates']],
    left_on='organism_id', right_on='ID',
    how='inner'
)
print(f"{len(specimen_join)} OTB fossils matched a published ECV measurement")
print(specimen_join[['catalog_number', 'taxon_name', 'ecv_median_cm3', 'n_estimates']]) 
# %% [markdown]
# # Why So Few Matches
# There are so few matches in this dataset because there are only 4 species in the OTB data which
# can match to those in the ECV data. The ECV data has much more taxanomic diversity to it.

# %% 4 - Pivot Table

bins   = [0.0, 1.0, 2.0, 2.6, 3.5]
labels = ['Late Pleistocene', 'Early Pleistocene', 'Plio-Pleistocene', 'Pliocene']

fossils_ecv['time_bin'] = pd.cut(fossils_ecv['earliest_chronometric_age'],
                               bins=bins, labels=labels)

pivot = fossils_ecv.pivot_table(
    values='ecv_mean',
    index='taxon_name',
    columns='time_bin',
    aggfunc='mean',
    observed=False
).round(1)
print(pivot)
# %% [markdown]
# # Interpretation
# From this table, it appears that mean ecv increased over time, however there a gaps in the data.

# %% 4: OTB + ECV Analysis

# %% 1 - Scatter Plot
# %% 1 - Scatter Plot
# Grade per taxon (most common grade in ecv_full)
taxon_grade = (
    ecv_full.groupby('taxon')['grade']
    .agg(lambda s: s.mode().iloc[0])
    .reset_index()
    .rename(columns={'taxon': 'taxon_name'})
)

# Mean OTB specimen age and ECV per taxon, only taxa with ECV data
taxon_age = (
    fossils_ecv.dropna(subset=['ecv_mean'])
    .groupby('taxon_name')
    .agg(mean_age=('earliest_chronometric_age', 'mean'),
         ecv_mean=('ecv_mean', 'first'))
    .reset_index()
)

plot_df = taxon_age.merge(taxon_grade, on='taxon_name', how='left')
print(plot_df)

grade_labels = {
    'archaic': 'Archaic australopith',
    'mega':    'Robust australopith / Paranthropus',
    'trans':   'Transitional (H. habilis)',
    'pre.mod': 'Pre-modern Homo'
}

fig, ax = plt.subplots(figsize=(8, 6))

for grade, sub in plot_df.groupby('grade'):
    ax.scatter(sub['mean_age'], sub['ecv_mean'], s=80,
               label=grade_labels.get(grade, grade))

for _, r in plot_df.iterrows():
    ax.annotate(r['taxon_name'], (r['mean_age'], r['ecv_mean']),
                textcoords='offset points', xytext=(6, 6), fontsize=9)

ax.set_xlabel('Mean specimen age (Ma)')
ax.set_ylabel('Mean ECV (cm³)')
ax.legend(title='Grade')

plt.tight_layout()
plt.show()

# %% 2 - Histogram
n = ecv_hominin['n_estimates']
bins_n = range(int(n.min()), int(n.max()) + 2)   # one bin per integer value

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(n.dropna(), bins=bins_n, align='left', edgecolor='black')

ax.set_xlabel('Number of ECV estimates per specimen (n_estimates)')
ax.set_ylabel('Number of specimens')
ax.set_xticks(list(range(int(n.min()), int(n.max()) + 1)))

plt.tight_layout()
plt.show()
print(n.describe())
print("Specimens with only 1 estimate:", (n == 1).sum(), "of", len(n))
# %% [markdown]
# # Histogram Interpretation

# %% 3 - OTB Locality Analysis
localities = pd.read_sql("SELECT locality_id, place, country FROM localities", engine)
fossils_ecv = fossils_ecv.merge(localities, on='locality_id', how='left')

diversity = (
    fossils_ecv.groupby(['locality_id', 'place'])['taxon_name']
    .nunique()
    .sort_values(ascending=False)
)
print(diversity.head(10))

top_id = diversity.index[0][0]
top_place = diversity.index[0][1]
loc_df = fossils_ecv[fossils_ecv['locality_id'] == top_id]

print("Locality:", top_place)
print("Fossils:", len(loc_df))
print(loc_df['taxon_name'].value_counts())

# One ecv_mean per taxon, so de-duplicate before summarizing
loc_taxa = loc_df.drop_duplicates('taxon_name')[['taxon_name', 'ecv_mean']]
print(loc_taxa)
print("Mean ECV across taxa:", round(loc_taxa['ecv_mean'].mean(), 1))
print("ECV range across taxa:",
      round(loc_taxa['ecv_mean'].min(), 1), "-", round(loc_taxa['ecv_mean'].max(), 1))
print("Taxa with ECV:", loc_taxa['ecv_mean'].notnull().sum(), "of", len(loc_taxa))
print("Age range (Ma):", loc_df['earliest_chronometric_age'].min(), "-",
      loc_df['earliest_chronometric_age'].max())
