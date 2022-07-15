from turtle import down
import pandas as pd


def link_source(model_place: str, source="WorldPop"):

    pop_path = "/home/jovyan/workspace/road_analytics/tradesman/data/population/all_raster_pop_source.csv"
    df = pd.read_csv(pop_path)

    if source == "WorldPop":

        return df[df.Country.str.upper() == model_place.upper()].worldpop_link.values[0]

    elif source == "Meta":

        return df[df.Country.str.upper() == model_place.upper()].meta_link.values[0]

    else:
        raise ValueError("No population source found.")
