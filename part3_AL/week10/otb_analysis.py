# %% [markdown]
# ## Why virtual environments matter
#
# A virtual envionment is an isolated directoy which contains a specific python interpreter and packages
# needed for specific project. I am using a virtual environment for this project to ensure that 
# packages in this project dont break codes from other projects and vice-versa
# %% Setup
import numpy as np
import pandas as pd
print(np.__version__, pd.__version__)


otb = pd.read_csv("otb_fossils.tsv", sep = '\t')

# %% Part 1 — language basics
# List Comprehensions
half = [x*0.5 for x in range(100)]
print(half)

# %% Dictionary Comprehensions
subregion_groups = {loc: rows for loc, rows in otb.groupby("subregion")}
subregion_counts = {loc: len(rows) for loc, rows in subregion_groups.items()}
for loc, n in subregion_counts.items():
    print(f"{loc}: {n}")

# %% zip/enumerate
for i, state in enumerate(['Marsabit', 'South Ethiopia', 'Turkana']):
    print(i, state)

prep_type = ['Tooth', 'Postcranium', 'Cranium', 'Mandible']
counts = [689, 261, 177, 120]
for prep, count in zip(prep_type, counts):
    print(f"{prep}: {count}")

# %% *args/**kwargs
specimens = pd.DataFrame({
    'id': ['NWJ-02', 'KME-12', 'ADF-39', 'MJL-11'],
    'prep': ['cranium', 'cranium', 'cranium', 'cranium'],
    'prepMassGrams': [590.212, 615.991, 650.123, 660.543],
    'foundBy': ['Jaworski', 'Jaworski', 'Jaworski', 'Jaworski']
})

def summarize(*fields, decimals=3):
    for f in fields:
        print(f"{f}: {round(specimens[f].mean(), decimals)}")

summarize('prepMassGrams')

# %% lambda
specimens['estimatedBrainSize'] = specimens['prepMassGrams'].apply(lambda x: 'Small' if x < 600 else 'Big')

# %% Part 2 — NumPy

# %% 1D array of 10 stratigraphic ages in Ma, print dtype, shape, and dnim and 
#convert to kiloyears using vectorized arithmetic
agesMa = np.array([3.05, 1.5, 1.42, 2.31, 1.9, 1.95, 4, 1.64, 1.46, 1.58])
print(agesMa)
print(agesMa.dtype)
print(agesMa.shape)
print(agesMa.ndim)

agesKa = agesMa*1000
print(agesKa)


# %% 2D array with 5 rows (specimens) and 3 columns repping different numeric 
#measurements/attributes. Demonstrate [1] slicing a single row & column, 
#[2] column-wise means using axis=0, and [3] row-wie standard deviaition using axis=1
# 5 specimens with 3 attributes (mass, volumn, age)
specimens_measurements = np.array([
    [56.3, 20.23, 3.05],
    [66, 78.2, 1.42],
    [23.25, 13.6, 1.46],
    [98.06, 150.2, 1.64],
    [54.6, 89.6, 2.31]
])
print(specimens_measurements)

# %% [1] Slicing a single row and a single column
row_2 = specimens_measurements[1]
print("Row 2:", row_2)        
col_mass = specimens_measurements[:, 0]  
print("Mass column:", col_mass)

# %% [2] Column-wise means
col_means = specimens_measurements.mean(axis=0)
print("Mean mass, volume, age:", col_means)

# $$ [3] Row-wise standard deviation
row_sds = specimens_measurements.std(axis=1)
print("SD per specimen:", row_sds)

# %% Using array from step 1, demonstrate [1] boolean indexing to select specimens 
#within a time window, [2] fancy indexing to select exactly 3 specimens by position, 
#[3] a compound boolean condition combining 2 constraints

# %% [1] Boolean Indexing to select specimens in time window
window = agesMa[(agesMa > 1.95) | (agesMa < 1.5)]
print(window)

# %% [2] Fancy indexing to select 3 specimens by position
idx = np.array([1, 4, 8])
print(agesMa[idx])

# %% [3] Compound boolean condition combining 2 constraints
compound = agesKa[(agesKa <= 2310) & (agesKa > 1420)]
print(compound)

# %% [markdown]
# Why NumPy operations are faster than Python loops
# NumPy is specifically designed to work with large arrays of data. It stores data independetly of built-in python
# objects, allowing its algorithms to work indepenedtly of Python's overhead. The C-based alorithms which make up NumPy avoid
# overhead present in regular Python for loops. If the dataset is smaller or there are multiple steps involved, then I would
# want to write a for loop.

# %% Part 3 - pandas

# %% Create a series of specimen counts by locality (5). Demonstrate label-based access, integer-position access, and
# boolean filtering on the series
locality_counts = pd.Series(
    [125, 428, 665, 780, 900],
    index=['Fejej', 'Ileret', 'Koobi Fora', 'Allia Bay', 'Brown Sands']
)
print(locality_counts.loc['Fejej'])
print(locality_counts.iloc[4])
print(locality_counts[locality_counts < 600])


# %% Create a DataFrame from a Pthon dict repping 8 fossil specimens with columns for:
# speciment ID, taxon, locality, stratigraphic age (Ma), and skeletal element.
# Demonstrate [1] df.info() and df.describe(), [2] .loc selection by a boolean condition,
# [3] .iloc selection by integer position

specimensDF = pd.DataFrame({
    'specimen_id': ['NWJ-123', 'KME-116', 'ADF-117', 'MJL-423', 'SJL-213', 'FJL-165', 'ABC-123', 'XYZ-789'],
    'taxon': ['Homo', 'Homo', 'Homo', 'Homo', 'Paranthropus', 'Australopithecus', 'Paranthropus', 'Australopithecus'],
    'locality': ['Fejej', 'Koobi Fora', 'Koobi Fora', 'Fejej', 'Brown Sands', 'Allia Bay', 'Allia Bay', 'Fejej'],
    'age_ma': [2.56, 4.11, 6.75, 2.57, 3.14, 5.12, 5.13, 5.40],
    'element': ['cranium', 'humerus', 'tooth', 'tibia', 'cranium', 'tarsal', 'pelvis', 'tooth']
})

print(specimensDF.info())
print(specimensDF.describe())
print(specimensDF.loc[specimensDF['age_ma'] >= 4, 'specimen_id'])
print(specimensDF.iloc[1:4, 3:5])


# %% Add 2 derived columns to DataFrame. One numeric column computed from existing column,
# and one categorical column derived from a condition

specimensDF['ageKa'] = specimensDF['age_ma']*1000
specimensDF['qualAge'] = specimensDF['age_ma'].apply(lambda x: 'Younger' if x < 3.5 else 'Older')
print(specimensDF)

# %% Demonstrate sorting and grouping. [1] Sort DF by a column and display the result, 
# [2] use groupby with at least 1 aggregation function to produce a meaningful summary table, 

specimensDF = specimensDF.sort_values('specimen_id')
print(specimensDF)

taxonGroups = specimensDF.groupby('taxon').agg(
    n_specimens = ('specimen_id', 'count'),
    mean_age_ma = ('age_ma', 'mean'),
    oldest_ma   = ('age_ma', 'max'),
)
print(taxonGroups)

# %% [markdown]
# Summary Interpretation
# My summary indicates that Homo are the most abundant specimens in my dataset. It also indicates a potential error. 
# Either the dating method was conducted wrong or someone entered data incoreectly because the oldest Homo specimen 
# should not be older than Australopithecus or Paranthropus

# %% Part 4 - OTB Analysis

# %% Load in OTB Fossils dada
df = pd.read_csv("otb_export_example.csv")
print(df)
print('df.shape')
print(df.shape)
print('df.dtypes')
print(df.dtypes)
print('df.isnull()')
print(df.isnull())
print('df.sum()')
print(df.sum())
print('df.describe()')
print(df.describe())
# %% [markdown]
# I am noticing some NaN vales in earlier_chronometric_age and latest_chronometric_age. Otherwise things seem normal

# %% Specimens Per Taxon
# Homo taxa are pretty well represented in this dataset, making up a seemingin majority of the data
taxon_counts = df["scientific_name"].value_counts()
print(taxon_counts)

# %% Chronometric Age Per Localty
# A majority of the fossils found are on average less than 3 million years old
df["avg_age"] = df[["earliest_chronometric_age", "latest_chronometric_age"]].mean(axis=1)
age_by_locality = df.groupby("place")["avg_age"].agg(["mean", "min", "max", "count"]).round(2)
print(age_by_locality.sort_values("mean"))

# %% Common Skeletal Elements
# Teeth are the commonly found skeletal elements, probabably thanks to their ability to preserve so well
element_counts = df["preparations"].value_counts()
print(element_counts)

# %% Single Taxa In A Locality
#Yes, there are 3 locations (Kanapoi, Lothagam, and South Turkwel) where all specimens are the same taxon
taxa_per_locality = df.groupby("place")["scientific_name"].nunique()
single_taxon = taxa_per_locality[taxa_per_locality == 1]
print(single_taxon)

# %% NumPy Array

ages = df["earliest_chronometric_age"].dropna().to_numpy()

mean = ages.mean()
sd   = ages.std()          # population SD; use ages.std(ddof=1) for sample SD

within_1sd = np.abs(ages - mean) <= sd
proportion = within_1sd.mean()

print(f"n = {ages.size}")
print(f"mean = {mean:.3f} Ma")
print(f"SD = {sd:.3f} Ma")
print(f"Proportion of specimens within 1 SD of the mean = {proportion:.3f}")

# %% Adding Epoch column
df['epoch'] = df['avg_age'].apply(lambda x: 'Pleistocene' if x < 2.58 else 'Pliocene')

taxon_by_epoch = (df.groupby("epoch")["scientific_name"]
                    .value_counts()
                    .unstack("epoch", fill_value=0))
print(taxon_by_epoch)
# %% Most specimens are coming from the Pleistocene