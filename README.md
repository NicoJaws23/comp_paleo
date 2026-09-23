## Project Title: Computational Paleobiology Data Summary Scripts.
This repository hold a number of scripts written for Denne Reed's 
Computational Paleobiology course from the Fall of 2026. The scripts give 
basic information on TSV files in within the subdirectories. Using these 
scripts, you can get basic data summaries (ex: number of specimens in a 
formation), ensure that TSV files have no empty cells/missing columns,
and get summaries on the structure of datasets.

## Course Context: 
Computational Paleobiology, The University of Texas at 
Austin, Fall 2026

## Repository Structure: 
The repository is divided into 3 sections, part1_OS, 
part2_DB, part3_AL. My director also has a subdirectory called PP_Data 
which holds some test data used for a personal project. The three parts 
each have 4 to 5 subdirectories related to tha weeks course content. 
part1 has subdirectories for week01-04, part2 has week05-09, and part3 has
week10-14. The useful shell scripts are all located in ~/comp_paleo/part1_OS/week04/
The other subdirectories contain text files for assignments and various
csv and tsv files. Useful files for the scripts are eppe_fossils.tsv and 
otb_fossils.tsv, located in the week04 subdirectory.

## Dependencies: 
All scripts are designed to run on bash and will work on
Linux and WSL. Important tools include awk, sed, grep, and cut.

## Usage:
All scripts can be run by calling ./<scriptName> and the necessary 
arguments. Should a user not input the correct or correct number of 
arguments, a message will appear telling the user how to properly use 
the script. Here are 2 usage examples:

dataset_info.sh
Usage: ./dataset_info.sh <filepath>
The script requires only a filepath of a TSV file to run after specifying 
the script.

check_catalog_numbers.sh
Usage: ./check_catalog_numbers.sh <tsv_file> <prefix>
This script requires the user to specify a TSV file and a catalog prefix 
present in the TSV file. 

## Data:
The datasets and scripts can be found within the subdirectories. 
Currently only Part1_OS/week04/ has scripts and it also has 2 TSV files 
(eppe_fossils.tsv, otb_fossils.tsv) which can be used for analysis.

## Author:
Nico Jaworski, nico.jaworski@utexas.edu 

