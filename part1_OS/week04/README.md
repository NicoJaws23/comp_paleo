This subdirectory contain the important scripts used to summarize and 
describe the data and data structures in eppe_fossils.tsv and 
otb_fossils.tsv, also found in this subdirectory. What follows is a 
description of each scripts:

hello_researcher.sh: This script is very simple and simply displays the 
date, the researcher, and current working directory. It is used by entering
./hello_researcher.sh

dataset_info.sh: This script takes  file and tells the user the filename, 
the number of rows, the number of columns, and the names of the columns. It 
is called by entering ./dataset_info.sh <filepath>

validate_tsv.sh: This script makes sure that each row of a tsv file had 
the expected number of columns and identifies which rows do not match the 
expectation. It is used by entering ./validate_tsv.sh <filepath> <expected_columns>

formation_counts.sh: This script prints out the number of speciment counts 
for a list of formations in the otb_fossils.tsv dataset. It is used by 
entering ./formation_counts.sh <tsv_file>

batch_inspect.sh: This script loops over files in a directory, report the 
number of tsv foles found, and then spits out the file names, number of 
rows, and number of columns. It is used by entering ./batch_inspect.sh <directory>

check_catalog_number.sh: This script proceess a file and searches for rows 
which have a catalog number starting with a given prefix. It is used by 
entering ./check_catalog_numbers.sh <tsv_file> <prefix>

dataset_report.sh: This script combines the previous scripts to go over a 
directory, find all the tsv files, print the filename, row count, column 
count, the names of the first 3 columns, and whether or not the file passed 
a validation check for. It also logs files with less than 100 rows and 
prints a summary of its findings. It is used by entering ./dataset_report.sh <directory>


