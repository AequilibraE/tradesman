from turtle import down
import pycountry

from tradesman.data.meta_pop_url import url_reducer


def link_source(model_place: str, source="WorldPop"):

    country_code = pycountry.countries.search_fuzzy(model_place)[0].alpha_3

    if source.lower() == "WorldPop".lower():

        return (
            "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/"
            + f"{country_code}/{country_code.lower()}_ppp_2020.tif"
        )

    elif source.lower() == "Meta".lower():

        return "https://cutt.ly/" + url_reducer[country_code]

    else:
        raise ValueError("No population source found.")
