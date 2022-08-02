CREATE TABLE IF NOT EXISTS political_subdivisions("country_name" TEXT,
                                                  "division_name" TEXT,
                                                  "level" INTEGER);

--#
SELECT AddGeometryColumn('political_subdivisions', 'geometry', 4326, 'MULTIPOLYGON', 'XY' );

--#
SELECT CreateSpatialIndex('political_subdivisions' , 'geometry' );