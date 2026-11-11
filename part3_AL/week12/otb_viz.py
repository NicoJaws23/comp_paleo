# %% Imports
import json
import os
import pandas as pd
from plotnine import *
from sqlalchemy import create_engine

from config import DSN

# %% Load data
engine = create_engine(DSN)

fossils = pd.read_sql(
    """
    SELECT f.*, t.scientific_name, l.*
    FROM fossils f
    JOIN taxa t USING (taxon_id)
    JOIN localities l USING (locality_id)
    """,
    engine
)

# set the path to the week 11 folder so the file can be located.
path = os.path.join("part3_AL/week11/ecv_by_specimen.csv")
ecv_full = pd.read_csv(path)

# Grade is a ordered categorical variable. 
# We need to set the ordering or else it will default
# to alphabetical. 
grade_order = ['archaic', 'mega', 'trans', 'pre.mod']
ecv_full['grade'] = pd.Categorical(ecv_full['grade'],
	categories=grade_order,
	ordered=True)
	
# %% Re-create taxon_map and fossils_ecv from Week 11
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

fossils['taxon_name']=fossils['scientific_name'].map(taxon_map)

ecv_by_taxon = (
    ecv_full
    .groupby('taxon')['ecv_median_cm3']
    .agg(ecv_mean='mean', ecv_median='median',
         ecv_min='min', ecv_max='max', ecv_n='count')
    .reset_index()
)

fossils_ecv = pd.merge(
    fossils,
    ecv_by_taxon,
    left_on='taxon_name', right_on='taxon',
    how='left'
)
print(fossils_ecv.shape)

# %% Part 1: Univariate Distributions

# %% 1.1 Histogram
# ECV distribution across all specimens in Du et al.
hist1 = (ggplot(ecv_full, aes(x='ecv_median_cm3'))
      + geom_histogram(binwidth=25, fill='steelblue', color='white')
      + labs(x='Endocranial volume (cm³)', y='Count',
             title='Distribution of hominin ECV estimates')
      + theme_bw()
)
hist1.save('part3_AL/week12/ecv_histogram50.png', dpi=150)

hist2 = (ggplot(ecv_full, aes(x='ecv_median_cm3'))
      + geom_histogram(binwidth=50, fill='steelblue', color='white')
      + labs(x='Endocranial volume (cm³)', y='Count',
             title='Distribution of hominin ECV estimates')
      + theme_bw()
)
hist2.save('part3_AL/week12/ecv_histogram25.png', dpi=150)

hist3 = (ggplot(ecv_full, aes(x='ecv_median_cm3'))
      + geom_histogram(binwidth=75, fill='steelblue', color='white')
      + labs(x='Endocranial volume (cm³)', y='Count',
             title='Distribution of hominin ECV estimates')
      + theme_bw()
)
hist3.save('part3_AL/week12/ecv_histogram75.png', dpi=150)

# %% [markdown]
# # Histograms With Different Bin Sizes
# ![Bin = 25](part3_AL/week12/ecv_histogram25.png)
# ![Bin = 50](part3_AL/week12/ecv_histogram50.png)
# ![Bin = 75](part3_AL/week12/ecv_histogram75.png)
# Changes in bin width communicate different amounts of variation in the counts of each ECV size. For example, when bin = 25, we see more variation in ecv compared to bin = 75 

# %% 1.2 Density Plot
densityPlot = (ggplot(ecv_full, aes(x='ecv_median_cm3', fill='grade'))
      + geom_density(alpha=0.4)
      + scale_fill_brewer(type='qual', palette='Set2')
      + labs(x='Endocranial volume (cm³)', fill='Grade')
      + theme_bw()
)
densityPlot.save('part3_AL/week12/ecv_density_by_grade.png', dpi=150)
# %% [markdown]
# # Density Plot Interpretations
# A. The pre-modern grade has the widest ecv range. The pre-modern grade may represent more invidiuals than the other grades, meaning there are more measurments/vairety. Additionally, the pre-modern grade may represent longer evolutionary time, as in we are seeing more changes relative to the other grades.
# B. The trans and pre-mod grades overlap from ecv values of 900 and below. This overlap may imply that taxonomic boundaries based on ecv alone may not be particurally informative, we need more points of evidence to distinguish between grades.

# %% Part 2: Bivariate Relationships

# %% 2.1 Scatter Plot
scatterPlot = (ggplot(ecv_full, aes(x='age_mid_Ma', y='ecv_median_cm3',
                            color='grade', size='n_estimates', shape='grade'))
      + geom_point(alpha=0.7)
      + scale_x_reverse()          # older ages on the left
      + scale_color_brewer(type='qual', palette='Set1')
      + labs(x='Age (Ma)', y='ECV (cm³)',
             color='Grade', shape='Grade', size='N estimates',
             title='Hominin ECV through time')
      + theme_bw()
)
scatterPlot.save('part3_AL/week12/ecv_vs_age.png', dpi=150)
# %% [markdown]
# # Why Add Shape Encoding for Grades?
# Adding a redundant shape encoding for grades makes it more accessible to those who are color blind or otherwise have a difficult time distinguishing between colors. Additionally, if this plot was printed in black and white it would still be readable thanks to the shape encoding.

# %% 2.2 Adding a Trend Line
scatterPlot2 = (ggplot(ecv_full, aes(x='age_mid_Ma', y='ecv_median_cm3'))
      + geom_point(aes(color='grade'), alpha=0.6)
      + geom_smooth(method='lm', color='black', linetype='dashed')
      + geom_smooth(aes(color='grade'), method='lm')
      + scale_x_reverse()
      + labs(x='Age (Ma)', y='ECV (cm³)')
      + theme_bw()
)
scatterPlot2.save('part3_AL/week12/ecv_trend.png', dpi=150)
# %% [markdown]
# # Within-Grad vs Overall Slope
# The overall trend shows an increase in ecv through time, however this is misleading. Pre-mod shares a similar slope to the overall trend, archaic and mega do increase over time but with a much shallower slope, and trans actually shows a decrease in ecv instead of an increase.
# %% 2.3 Boxplot by Taxon
# Order taxa by median ECV
taxon_order = (ecv_full.groupby('taxon')['ecv_median_cm3']
               .median()
               .sort_values()
               .index.tolist())

ecv_full['taxon'] = pd.Categorical(ecv_full['taxon'],
                                    categories=taxon_order,
                                    ordered=True)

boxPlot = (ggplot(ecv_full, aes(x='taxon', y='ecv_median_cm3', fill='grade'))
      + geom_boxplot()
      + coord_flip()               # horizontal boxes, easier to read long labels
      + labs(x='', y='ECV (cm³)', fill='Grade')
      + theme_bw()
      + theme(legend_position='bottom')
)
boxPlot.save('part3_AL/week12/ecv_boxplot_taxon.png', dpi=150)
# %% [markdown]
# # Boxplot Analysis
# H. erectus has the greatest within-taxon ECV variance. There may simply be more H. erectus specimens in this dataset, providing a greater number of datapoints. H. habilis, P. robustus, and P. boisei show substantial overlap, suggesting that ECV may not be the best taxanomic discriminator, more lines of evidence are needed to separate these species.

# %% Part 3: OTB Data

# %% 3.1 Species Counts by Taxon and Locality
counts = (fossils_ecv
          .groupby(['taxon_name', 'subregion'])
          .size()
          .reset_index(name='n_specimens'))

otb_col = (ggplot(counts, aes(x='subregion', y='n_specimens', fill='taxon_name'))
      + geom_col()                 # stacked bar (geom_col uses a pre-computed y)
      + coord_flip()
      + labs(x='', y='Specimens', fill='Taxon')
      + theme_bw()
      + theme(legend_position='bottom',
              figure_size=(8, 5))
)
otb_col.save('part3_AL/week12/otb_counts.png', dpi=150)

otb_col2 = (ggplot(counts, aes(x='subregion', y='n_specimens', fill='taxon_name'))
      + geom_col(position='dodge')                 # stacked bar (geom_col uses a pre-computed y)
      + coord_flip()
      + labs(x='', y='Specimens', fill='Taxon')
      + theme_bw()
      + theme(legend_position='bottom',
              figure_size=(8, 5))
)
otb_col2.save('part3_AL/week12/otb_counts2.png', dpi=150)
# %% [markdown]
# # I would want to use stacked bars to show the total number of specimens per site while also showing the proportion of each taxa per locality. I would want to use dodged bars to show how many of a distinct group are present at each site, not just the total number of specimens

# %% 3.2 Faceting
# Find taxa with 2 or more specimens
taxon_counts = ecv_full['taxon'].value_counts()
multi_specimen_taxa = taxon_counts[taxon_counts > 1].index

facet = (ggplot(ecv_full[~ecv_full['taxon'].isin(['Au. sediba', 'Au. garhi'])],
		aes(x='age_mid_Ma', y='ecv_median_cm3', color='grade'))
	+ geom_point(alpha=0.6)
	+ geom_smooth(method='lm', se=False, linetype='dashed', size=0.8)
	+ facet_wrap('~taxon', scales='free_y')
	+ scale_x_reverse()
	+ labs(x='Age (Ma)', y='Median ECV (cm³)')
	+ theme_bw()
	+ theme(legend_position='bottom',
		figure_size=(10, 6))
)
facet.save('part3_AL/week12/otb_ecv_faceted.png', dpi=150) 
# %% [markdown]
# # Within Taxon Trend
# For P. aethiopicus ECV increases with age, while for H. habilis ECV decreases with age.

# %% 3.3 Deliverable Heatmap
# %% 3.3 Deliverable Heatmap
heat_counts = (fossils_ecv
               .groupby(['taxon_name', 'place'])
               .size()
               .reset_index(name='n_specimens'))

heatmap = (ggplot(heat_counts, aes(x='taxon_name', y='place', fill='n_specimens'))
           + geom_tile(color='white')
           + scale_fill_gradient(low='#f7fbff', high='#08306b')
           + labs(x='Taxon', y='Locality', fill='Specimens')
           + theme_bw()
           + theme(axis_text_x=element_text(rotation=45, ha='right'),
                   figure_size=(8, 6))
)
heatmap.save('part3_AL/week12/fossils_ecv_heatmap.png', dpi=150)
# %% [markdown]
# # Heatmap Interpretation
# The Au. anamensis specimens from Kanapoi and H. erectus, H. habilis, Hominini, and Homo from Ileret and Koobi Fora are most represented. K. platyops is largely absent as are some of the Paranthropine specimens. This pattern suggests there is a sampling bias towards Homo specimens.

# %% Figure Quality
top = ecv_full.loc[ecv_full['ecv_median_cm3'].idxmax()]
low = ecv_full.loc[ecv_full['ecv_median_cm3'].idxmin()]

improvedFig = (ggplot(ecv_full, aes(x='age_mid_Ma', y='ecv_median_cm3'))
      + geom_point(aes(color='grade'), alpha=0.6)
      + geom_smooth(method='lm', color='black', linetype='dashed')
      + annotate('text', x=top['age_mid_Ma'] + 0.1, y=top['ecv_median_cm3'],
            label=f"{top['taxon']}\n({top['ecv_median_cm3']:.0f} cm³)",
            ha='right', size=9)
      + annotate('text', x=low['age_mid_Ma'] - 0.1, y=low['ecv_median_cm3'] - 130,
            label=f"{low['taxon']}\n({low['ecv_median_cm3']:.0f} cm³)",
            ha='left', size=9)
      + scale_x_reverse(breaks=[3, 2, 1, 0],
                   labels=lambda b: [f'{v:.1f} Ma' for v in b])
      + scale_y_continuous(breaks=range(250, 1501, 250),
                     labels=lambda b: [f'{v:.0f} cm³' for v in b])
      + coord_cartesian(xlim=(3.5, 0), ylim=(150, 1500))
      + scale_color_manual(values=['#E69F00', '#009E73', '#0072B2', '#D55E00'],
                     labels=['Archaic', 'Mega', 'Trans', 'Pre-modern'])
      + labs(x='Age (Ma)', y='ECV (cm³)', color='Grade', caption='Sources: Du et al. 2018; Reed et al. 2026', title='Change in ECV Over Time')
      + theme_bw()
      + theme(axis_text=element_text(size=11),
              axis_title=element_text(size=12),
              plot_title=element_text(size=14, weight='bold'))
      )

improvedFig.save('part3_AL/week12/publication_figure.png', dpi=300, width=7, height=5)
# %% [markdown]
# # Figure Choices
# Color Palette: I went with the Okabe-Ito color palette to make the figure accessible to color blind individuals.
# Axis-Ticks: I formatted my x-axis ticks to include Ma after each value. I also reformatted my y-axis to have cm3 after each value and added more breaks so viewers may have an easier time interpreting the rough size of each specimen.
# Annotation: I added annotation for the smallest and biggest ECV sizes, noting the taxon and size so viewers can get a sense of the range of ECV sizes.
# Caption: I simply captioned the Du et al. 2018 and Reed et al. 2026 publications to credit the data sources for the figure
# Font Size: I set my axis titles slightly larger than the axis labels to make sure they stood out. I also bolded and increased the size of the plot title for this same purpose.low