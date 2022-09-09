CREATE TABLE IF NOT EXISTS hex_pop(hex_id INTEGER,
                                   division_name TEXT,
                                   geo_wkt TEXT,
                                   population INTEGER);

--#
SELECT AddGeometryColumn('hex_pop', 'geometry', 4326, 'POLYGON', 'XY' );

--#
SELECT CreateSpatialIndex('hex_pop' , 'geometry' );