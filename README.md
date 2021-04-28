<h1 align="center">GeoWatch Labs - Market</h1>
<p align="center">

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About the project](#about-the-project)
  - [Goal](#goal)
  - [Data sources](#data-sources)
  - [Scores](#scores)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Create your pipenv](#create-your-pipenv)
- [Data exploration](#data-exploration)
  - [FSMS](#fsms)
  - [Geospatial data](#geospatial-data)
  - [Prices](#prices)

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
|<p align="center"> Tagant | <p align="center">  MoudjÃ©ria |
|<p align="center"> Assaba | <p align="center">  BoumdeÃ¯d, Kankossa, GuÃ©rou, BarkÃ©ol, Kiffa |
|<p align="center"> Gorgol | <p align="center">  M'Bout, Monguel |
|<p align="center"> Guidimaka | <p align="center">  Ould YengÃ©, SÃ©libaby |
|<p align="center"> Hodh el Gharbi | <p align="center">  Tamchakett, AÃ¯oun, Kobenni, Tintane |
|<p align="center"> Hodh ech Chargui | <p align="center">  TimbÃ©dra, NÃ©ma, Bassikounou, Amourj, Djiguenni |

### Data sources

Three categories of data sources will be used in this project :
 - FSMS data 
 - Geospatial data 
 - Prices data 

See [Data exploration](#data-exploration) for more information.

### Scores

## Getting started


### Prerequisites

-   Python 3.9 (or more recent)
-   [pipenv](https://pypi.org/project/pipenv/)

### Create your pipenv

Open your terminal, and install pipenv with:
```shell
pip install pipenv
```

Then, from the `src` directory, type:
```shell
pipenv install
```

This will create the virtualenv for this project, with the correct packages and versions.

Then type:
```shell
pipenv shell
```

To activate the virtualenv. And that's all !

**<u>WARNING :</u>**
When installing a package, you now have to use `pipenv install` instead of `pip install`. 
Once you've installed all you needed, you type `pipenv update`. It will update the `Pipfile`.

**<u>NB :</u>**
If you're using Pycharm, there are some extensions to use `pipenv` directly from your IDE.




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
| [FAO](https://fpma.apps.fao.org/giews/food-prices/tool/public/#/dataset/domestic) |    |    |   |   | Thibaut  |
| [Food security portal](https://api.foodsecurityportal.org/organization/food-security-portal) |    |  |   |   | Simon  |
| [FAO prices in Africa (.zip in Slack)](https://data-for-good.slack.com/archives/C01UPA0HKCY/p1618946330008000) |  |   | yearly  | country  | Hadrien  |
                     

The column "indice" represent the pricing indice that can be computed with this data source (CPI, price of a typical food basket, price of basic food ...)

<u><b>NB :</b></u> the column "who added this link" is here in case you want to ask questions about the source to the person who found it
