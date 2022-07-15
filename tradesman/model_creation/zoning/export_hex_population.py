def export_hex_population(project, zones_with_pop):
    zones_with_pop["geo"] = zones_with_pop.geometry.to_wkb()
    zones_with_pop = zones_with_pop.rename(columns={"division_name": "country_subdivision"})

    zones_with_pop[["hex_id", "country_subdivision", "x", "y", "population", "geo"]].to_sql(
        "hex_pop", project.conn, if_exists="replace", index=False
    )

    project.conn.execute("SELECT AddGeometryColumn('hex_pop', 'geometry', 4326, 'POLYGON', 'XY' );")
    project.conn.execute("SELECT CreateSpatialIndex('hex_pop' , 'geometry');")

    project.conn.execute("UPDATE hex_pop SET geometry=GeomFromWKB(geo, 4326);")

    project.conn.execute("Alter table hex_pop DROP COLUMN geo;")
    project.conn.commit()
