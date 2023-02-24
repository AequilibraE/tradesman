def saves_hex_pop_to_file(project, zones_with_pop):
    """
    Saves hexbins with population into open project.

    Parameters:
         *project*(:obj:`aequilibrae.project`): currently open project
         *zones_with_pop`(:obj:`geopandas.GeoDataFrame`): GeoDataFrame containing zones with population
    """
    zones_with_pop["geo_wkt"] = zones_with_pop.geometry.to_wkt()

    zones_with_pop[["hex_id", "division_name", "population", "geo_wkt"]].to_sql(
        "hex_pop", project.conn, if_exists="append", index=False
    )

    project.conn.execute("UPDATE hex_pop SET geometry=CastToMulti(GeomFromText(geo_wkt, 4326));")
    project.conn.execute("UPDATE hex_pop SET geo_wkt=NULL")
    project.conn.commit()
