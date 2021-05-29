<h1 align="center">GeoWatch Labs - Market</h1>
<p align="center">

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Getting started](#getting-started)
  - [Repository structure](#repository-structure)
    - [Config](#config)
    - [Import functions](#import-functions)
    - [Preprocessing functions](#preprocessing-functions)
    - [Utils](#utils)
- [About the project](#about-the-project)
  - [Goal](#goal)
  - [Data sources](#data-sources)
  - [Scores](#scores)
- [Data exploration](#data-exploration)
  - [FSMS](#fsms)
  - [Geospatial data](#geospatial-data)
  - [Prices](#prices)
  



____________________________________________________________________

## Getting started

### Repository structure

Our repository structure is the following :

```
├── config
|    ├── aggregation.py
|    └── preprocessing.py
├── import_functions
|    ├── automatic_analysis_and_aggregation.py
|    ├── auxiliary_function_for_geo_files.py
|    ├── auxiliary_function_for_importing_data.py
|    └── manual_aggregation.py
├── notebooks
|    ├── faodata.ipynb
|    ├── geoviz.ipynb
|    ├── mean_of_communes_yield.ipynb
|    └── study_data_types_preprocessing.ipynb
├── preprocessing
|    └── preprocessing.py
└── utils
    └── tiff_to_geojson.py
```

#### Config

Config folder is about all variables we setup for the project.


#### Import functions

Those are the functions extracting data from the zipfile and aggregating it into a csv file. 

The most important code here is `manual_aggregation`, reading all files from the main zip, unzipping them and standardizing 
column names according to manual inputs the team made in a csv, and aggregating it.

<p align="center">
  <img src="https://github.com/dataforgoodfr/batch9_geowatchlabs-3-markets/blob/main/doc/manual_aggregation_readme.png"/>
</p>

It generates a standardized dataframe, and a metadata dataframe.

⚠️ `manual_aggregation` may seem similar to `automatic_analysis_and_aggregation`, but it's not. `automatic_analysis_and_aggregation`
 aims at matching columns based on levenstein distance.

#### Preprocessing functions

Those are the functions reading the csv file and imputing missing values, standardizing data types and data before 
analysis and clustering. 

#### Utils

Additional functions that can be useful for some operations.


____________________________________________________________________


## About the project

### Goal

Study the influence of food price variations and other economic considerations (import, export, etc.) on food insecurity 
in the South agropastoral zone of Mauritania. 

The goal is to find a relationship that enables us to accurately estimate food insecurity situation there.

Studied moughataas, by region :

| region  | moughataas |
|---------|------------|
|<p align="center"> Trarza | <p align="center">  Ouad-Naga, Boutilimit |
|<p align="center"> Brakna | <p align="center">  Magta-Lahjar, Aleg |
|<p align="center"> Tagant | <p align="center">  Moudjeria |
|<p align="center"> Assaba | <p align="center">  Boumdeïd, Kankossa, Guerou, Barkeol, Kiffa |
|<p align="center"> Gorgol | <p align="center">  M'Bout, Monguel |
|<p align="center"> Guidimaka | <p align="center">  Ould Yenge, Selibaby |
|<p align="center"> Hodh el Gharbi | <p align="center">  Tamchakett, Aïoun, Kobenni, Tintane |
|<p align="center"> Hodh ech Chargui | <p align="center">  Timbédra, Néma, Bassikounou, Amourj, Djiguenni |

### Data sources

Three categories of data sources will be used in this project :
 - FSMS data 
 - Geospatial data 
 - Prices data 

See [Data exploration](#data-exploration) for more information.

### Scores

____________________________________________________________________

## Data exploration

### FSMS

Make sure to have `Mauritania FSMS data.zip` in your `$HOME`. The directory `Mauritania FSMS data` looks like this : 

```
Mauritania FSMS data
├── year
│    ├── monthYY
│    │     ├── data.sav
│    │     ├── pdf_1
│    │     └── pdf_2
[...]
```

We will here use the `.sav` files for our analysis. The script `Mauritania_FSMS_aggregation.py` aims at normalizing 
the data in this folder.

### Geospatial data

- GeoJSON of the studied zone
- .tiff : births, population, roads, railways ... (uploaded by Simon on the Google Drive)

### Prices

Here are the different pricing sources that we've collected so far :
     

| link  | indice | type of data  | frequency  | geographic level  | who added this link |
|-------|--------|---------------|------------|-------------------|---------------------|
| [World Food Program](https://data.humdata.org/dataset/wfp-food-prices-for-mauritania?force_layout=desktop) |    | price by crop | yearly | market  | Lucas  |
| [World Bank](https://data.worldbank.org/country/MR) |    |    |   | country  | Lucas  |
| [FAO](https://fpma.apps.fao.org/giews/food-prices/tool/public/#/dataset/domestic) |    |    |   |   | Thibaut  |
| [Food security portal](https://api.foodsecurityportal.org/organization/food-security-portal) |    |  |   |   | Simon  |
| [FAO prices in Africa (.zip in Slack)](https://data-for-good.slack.com/archives/C01UPA0HKCY/p1618946330008000) |  |   | yearly  | country  | Hadrien  |
                     

The column "indice" represent the pricing indice that can be computed with this data source (CPI, price of a typical food basket, price of basic food ...)

<u><b>NB :</b></u> the column "who added this link" is here in case you want to ask questions about the source to the person who found it

We used the [World Food Program] source as it is the most granular and comprehensive for Mauritania.
