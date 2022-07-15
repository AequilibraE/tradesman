def query_writer(df, tag="building", func="set_zero", is_area=False):

    qry = "UPDATE zones SET "

    for element in df.groupby(tag).count().index:

        if func == "set_zero" and is_area is False:
            qry += "osm_" + element + f"_{tag}=0, "
        elif func == "set_zero" and is_area is True:
            qry += "osm_" + element + f"_{tag}_area=0, "
        elif func == "set_value" and is_area is False:
            qry += "osm_" + element + f"_{tag}=?, "
        else:
            qry += "osm_" + element + f"_{tag}_area=?, "

    qry = qry[:-2] + " WHERE zone_id=?;"

    return qry
