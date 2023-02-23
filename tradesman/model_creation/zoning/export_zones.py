def export_zones(zone_data, project):
    """
    Saves zones with population into project.

    Parameters:
         *zone_data*(:obj:`geopandas.GeoDataFrame`): GeoDataFrame with zones and population info
         *project*(:obj:`aequilibrae.project`): currently open project
    """
    max_zone = zone_data.index.max()

    min_node = project.conn.execute("Select min(node_id) from nodes").fetchone()[0]

    if min_node <= max_zone:
        increment = project.conn.execute("Select max(node_id) from nodes").fetchone()[0] + 1
        project.conn.execute("update nodes set node_id =node_id + ?", [increment])
        project.conn.commit()

    zoning = project.zoning
    for zone_id, row in zone_data.iterrows():
        zone = zoning.new(zone_id)
        zone.geometry = row.geometry
        zone.population = row.population
        zone.save()
        # None means that the centroid will be added in the geometric point of the zone
        # But we could provide a Shapely point as an alternative
        # zone.add_centroid(False)
        # zone.save()
        # zone.connect_mode(mode_id="c", connectors=1)
