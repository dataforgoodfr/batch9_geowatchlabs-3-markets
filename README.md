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


## About the project

### Goal

Study the relationship between food price and food insecurity in Mauritania.

### Data sources

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