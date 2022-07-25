CREATE TABLE IF NOT EXISTS "raw_population" ("longitude" REAL,
                                             "latitude" REAL,
                                             "population" REAL);

--#
select AddGeometryColumn( 'raw_population', 'geometry', 4326, 'POINT', 'XY', 0);

--#
SELECT CreateSpatialIndex( 'raw_population' , 'geometry' );