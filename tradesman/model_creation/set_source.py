def set_source(source: str):

    if source.lower() == "WorldPop".lower():
        return "WorldPop"
    elif source.lower() == "Meta".lower():
        return "Meta"
    else:
        raise ValueError("No population source found.")
