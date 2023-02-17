def set_population_source(source: str):
    if source.lower() == "worldpop":
        return "WorldPop"
    elif source.lower() == "meta":
        return "Meta"
    else:
        raise ValueError("No population source found.")


def set_political_boundaries_source(source: str):
    if source.lower() == "gadm":
        return "GADM"
    elif source.lower() == "geoboundaries":
        return "GeoBoundaries"
    else:
        raise ValueError("Source not available.")
