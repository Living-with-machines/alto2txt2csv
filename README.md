# alto2txt2csv

This is a (very) small code library for converting and enhancing Historical British Newspapers. 

## Data

The newspaper data associated with these scripts can be found on Zenodo
- Living with Machines Digitised Newspapers [link](https://zenodo.org/records/15056078)
- Heritage Made Digital Digitised Newspapers [link](https://zenodo.org/records/15056046)

## Overview

This repository contains three notebooks.

- `process_newspaper.ipynb`: convert alto2txt output to a structure csv file
- `create_metadata.ipynb`: gather metadata for a newspaper title and write to a csv file
- `contextualize_newspaper.ipynb`: merge content dataframe with metadata 

The code below is taken from `contextualize_newspaper.ipynb` and shows how to merge newspaper content with reference data.

```python
nlp = '0002980' # select a newspaper title to process by NLP id
collections = 'lwm' # 'hmd' | 'lwm' select collection to process to which the title belongs
root_dir = '/path/to/newspaper/data' # path to the folder containing the csv folders
df = pd.read_csv(f'{root_dir}/{collections}-csv/{nlp}.csv') # read the csv file for the selected title
df_metadata = pd.read_csv(f'{root_dir}/{collections}-metadata/{nlp}_metadata.csv') # read the metadata file for the selected title
df_merged = add_context(df, df_metadata)
```