def amenity_count_query(df, **kwargs):

    qry = "UPDATE zones SET "

    if "set_zero" in kwargs.values():
        for element in df.columns[:-1]:
            qry += f"osm_{element}_amenity=0, "
    else:
        for element in df.columns[:-1]:
            qry += f"osm_{element}_amenity=?, "

    return qry[:-2] + " WHERE zone_id=?;"


def building_area_query(df, **kwargs):

    qry = "UPDATE zones SET "

    if "set_zero" in kwargs.values():
        for element in df.columns[:-1]:
            qry += f"osm_{element}_building_area=0, "
    else:
        for element in df.columns[:-1]:
            qry += f"osm_{element}_building_area=ROUND(?,2), "

    return qry[:-2] + " WHERE zone_id=?;"


def building_count_query(df, **kwargs):

    qry = "UPDATE zones SET "

    if "set_zero" in kwargs.values():
        for element in df.columns[:-1]:
            qry += f"osm_{element}_building=0, "
    else:
        for element in df.columns[:-1]:
            qry += f"osm_{element}_building=?, "

    return qry[:-2] + " WHERE zone_id=?;"
