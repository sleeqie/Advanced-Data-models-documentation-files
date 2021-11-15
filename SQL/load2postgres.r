
# setup -------------------------------------------------------------------
require(RPostgres) # also: RPostgreSQL::PostgreSQL()
require(sf)

# data --------------------------------------------------------------------
hood = st_read('PostGIS/data/geo/GEO_DATA/neighborhoods.shp')
shop = read.csv('PostGIS/data/geo/GEO_DATA/coffee_shops.csv')

# write -------------------------------------------------------------------
drv = RPostgres::Postgres()
con = dbConnect(drv,
                host = '139.14.20.252',
                port = 5433,
                dbname = 'mod3',
                user = 'student',
                password = 'tYXL5293091a2LGMkIsp')

dbSendQuery(con, "CREATE SCHEMA mod3_demo;")

dbWriteTable(con,
             name = 'coffee_shops',
             value = shop, row.names = FALSE, overwrite = TRUE)

st_write(hood, dsn = con, layer = 'neighborhoods')

dbDisconnect(con)
dbUnloadDriver(drv)
