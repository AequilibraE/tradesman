def saves_hex_pop_to_file(project, zones_with_pop):
    zones_with_pop["geo_wkt"] = zones_with_pop.geometry.to_wkt()
    zones_with_pop = zones_with_pop.rename(columns={"division_name": "country_subdivision"})

    zones_with_pop[["hex_id", "country_subdivision", "population", "geo_wkt"]].to_sql(
        "hex_pop", project.conn, if_exists="append", index=False
    )

    project.conn.execute("UPDATE hex_pop SET geometry=GeomFromText(geo_wkt, 4326);")
    project.conn.execute("UPDATE hex_pop SET geo_wkt=NULL")
    project.conn.commit()
