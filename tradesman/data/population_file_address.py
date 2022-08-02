from turtle import down
import pycountry
import pandas as pd


def link_source(model_place: str, source="WorldPop"):

    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    if source.lower() == "WorldPop".lower():

        return (
            "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/"
            + f"{country_code}/{country_code.lower()}_ppp_2020.tif"
        )

    elif source.lower() == "Meta".lower():

        df = pd.read_csv("/population/all_raster_pop_source.csv")

        return df[df.iso_country == country_code].meta_link

    else:
        raise ValueError("No population source found.")
