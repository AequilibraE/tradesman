# Geospatial Planning & Budgeting Platform Transport: Road Network Analytics

A set of Jupyter notebooks to support Road network analytics based on Open-Source and Open-Data
[Geospatial Planning & Budgeting Platform (GPBP) Transport sector use cases](https://docs.google.com/document/d/1AugI7_AiD2v-ES_actmseHsFMmi-oMdLxGF2YAcv5XY)

[FULL DOCUMENTATION IS AVAILABLE](https://pedrocamargo.github.io/road_analytics/), but a
quick preview of the resources developed is provided below:

# Notebooks

The notebooks are divided in four separate groups, from building the analytics 
models from a variety of data sources to computing estimates of the impact of 
changes to the transportation network. 

## 1 Building the analytics model

Performs all the data import

Quick summary statistics on the road model can be seen explored:
[VISUALIZE IT!](https://nbviewer.org/github/pedrocamargo/road_analytics/blob/main/notebooks/use_case-Descriptive_analytics_ROADS.ipynb)

Quick summary statistics on the population data loaded can also be seen explored:
[VISUALIZE IT!](https://nbviewer.org/github/pedrocamargo/road_analytics/blob/main/notebooks/use_case-Descriptive_analytics_POPULATION.ipynb)



### 1.1 Importing the OSM network

**In a nutshell**: Imports the OSM network into a computationally-efficient 
format

We can see the imported result on a browser 
[VISUALIZE IT! (it may take time to open)](https://nbviewer.org/github/pedrocamargo/road_analytics/blob/main/notebooks/1.1_Build_model_from_OSM.ipynb)

### 1.2 Importing Population data

**In a nutshell**: Imports population data from Raster format into a 
computationally-efficient and aggregated into customizable polygons

#### 1.2.1 Importing raw population data

**In a nutshell**: Imports population data from Raster format into 
a vector format

A heatmap shows the distribution of the population [VISUALIZE IT!](https://nbviewer.org/github/pedrocamargo/road_analytics/blob/main/notebooks/1.2.1_Vectorizing_population.ipynb)

#### 1.2.2 Aggregating population into analysis zones

**In a nutshell**: Aggregates population data into analysis zones
with geographic resolution proportional to population density

[VISUALIZE IT!](https://nbviewer.org/github/pedrocamargo/road_analytics/blob/main/notebooks/1.2.2_Population into hex and clustering.ipynb)


### 1.3 Importing Point-of-Interest data

**In a nutshell**: Imports several classes of Point-of-Interest data
from OSM into the model's database

This jupyter notebook includes the visualization of all hospitals, schools
and airports imported and can visualized -> **UNDER DEVELOPMENT**

## 2 Building the transport model

Begins the modelling process per se by incorporating a series of
assumptions aligned with best-practices from the transport modelling world
to turn the analytics model into a simplified transport model capable of
providing traffic estimates for any link in the road network model.

### 2.1 Augmenting the road network model

**In a nutshell**: Assign speeds and road capacities as a function of road
type and pavement type/condition.

This jupyter notebook includes a map showing the routes in the network 
with the highest capacity and can visualized. 
[VISUALIZE IT!](https://nbviewer.org/github/pedrocamargo/road_analytics/blob/main/notebooks/2.1_augments_network_data.ipynb)

### 2.2 Implementing a simplified transport model

**In a nutshell**: Produces transportation demand matrices based on 
the population and PoI imported

This jupyter notebook includes a map showing the traffic distribution in 
an abstract map that effectively shows the overall traffic demand 
across the network and can visualized -> UNDER DEVELOPMENT.

## 3 Mobility data

**In a nutshell**: Incorporates mobility data to calibrate and/or replace
the simplified demand model developed on **2.2**

### 3.1 Creation of transport demand matrices from CVTS

**In a nutshell**: Processes the CVTS data for Vietnam to obtain trip
matrices that can be used in conjunction with the personal travel 
demand matrices produced on **2.2**.

## 4 Use-cases

**In a nutshell**: Generalizable use-cases that may be of interest in 
multiple countries

### 4.1 Link traffic estimate

**In a nutshell**: Computes the an estimate of the traffic for any given link.
It also allows for extracting the origins and destinations using said link/asset

**NOTEBOOK UNDER DEVELOPMENT.**

### 4.2 Bottleneck identification

**In a nutshell**: Identifies the sections (links/assets) in the network that 
are most likely to be bottlenecks as a function of their capacity and estimated
traffic volumes.

**NOTEBOOK UNDER DEVELOPMENT.**

### 4.3 Link criticality analysis for links with the highest capacity

**In a nutshell**: Computes the impact of the disruption of each one of the 
10% of links with the highest demand (can use either synthetic data or from 
mobility data)

**NOTEBOOK UNDER DEVELOPMENT.**

### 4.4 Impact of flooding into hospital access

**In a nutshell**: Identifies the population cut-off from hospital access for
a given flooding scenario

**NOTEBOOK UNDER DEVELOPMENT.**
