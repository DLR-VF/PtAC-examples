import os
import sys
from time import process_time

import geopandas as gpd
import pandas as pd

from ptac import accessibility as accessibility
from ptac import osm as osm
from ptac import population as population

for path, dirnames, filenames in os.walk('data'):
    #print(path, dirnames, filenames)
    #if not dirnames.startswith('.'):
    for city in dirnames:
        if not city.startswith('.'):
            #print(city)
            pn = os.path.join(path, city)
            #print(pn)
            if os.path.exists(pn + f'/{city}_Boundary.shp'):
                # Read and save boundary:
                print(f"Reading city boundary of {city}...")
                gdf_place = gpd.read_file(pn + f"/{city}_Boundary.shp")
                #print(f"Saving city boundary of {city} as a geopackage ...")
                boundary_gdf_place = gdf_place.to_crs('EPSG:4326').copy()
                boundary_gdf_place.to_file(pn + f"/{city}_Boundary.gpkg", driver="GPKG", OVERWRITE='YES')
                boundary = gpd.read_file(pn + f"/{city}_Boundary.gpkg")

                # Download and save the road network:
                print(f"Downloading street network of {city} ...")
                network_gdf_place = osm.get_network(boundary).copy()
                network_gdf_place.to_file(pn + f"/{city}_network.gpkg", driver="GPKG")
                #print("City networks...")
                network = gpd.read_file(pn + f"/{city}_network.gpkg")
                print(f"Downloaded street network of {city}")

            else:
                print(f'File {city} boundary not found. Check the name of file.')
                break

            if os.path.exists(pn + f'/{city}_Population.tif'):
                # Convert population raster population points:    
                print(f"Converting population raster of {city} to population points ...")
                population_points = population.raster_to_points(pn + f"/{city}_Population.tif")  
                population_points = population_points[population_points['pop']>0]
                population_points['pop'] = population_points['pop']/ 1000
                #print(population_points.head())
                # Clip and save populaints:
                #print(f"Clipping population points of {city} with boundary ...")
                population_points_clip = gpd.clip(population_points, boundary_gdf_place).copy()
                population_points_clip.to_file(pn + f"/{city}_pop_points_clip_10m.gpkg", driver="GPKG")
                gdf_population = gpd.read_file(pn + f"/{city}_pop_points_clip_10m.gpkg")
            else:
                print(f'File {city} population not found. Check the name of file.')
                break

            if os.path.exists(pn + f'/{city}_Busstops.shp'):
                # Read and save public transport stops:
                print(f"Reading bus stops of {city}...")
                df_bustops = gpd.read_file(pn + f"/{city}_Busstops.shp")
                stops_low_capacity = df_bustops.to_crs('EPSG:4326').copy()
                stops_low_capacity_clip = gpd.clip(stops_low_capacity, boundary).copy()
                stops_low_capacity_clip.to_file(pn + f"/{city}_low_capacity_stops.gpkg", driver="GPKG")
                stops_low_capacity_clip = gpd.read_file(pn + f"/{city}_low_capacity_stops.gpkg").copy()

                print("Calculating accessibility to low-capacity public transit systems ...")
                accessibility_output_low = accessibility.distance_to_closest(
                                            start_geometries=gdf_population,
                                            destination_geometries=stops_low_capacity_clip,
                                            boundary_geometries=boundary,
                                            network_gdf=network,
                                            number_of_threads=4,
                                            transport_system="low-capacity",
                                            verbose=1)
                #print(f"Accessibility calculated for {city} low-capacity transit system")

                accessibility_output_low.to_file(pn + f"/{city}_output_low_capacity_without_gtfs.gpkg", driver="GPKG")
                output_low = gpd.read_file(pn + f"/{city}_output_low_capacity_without_gtfs.gpkg")
                sdg_low = accessibility.calculate_sdg(df_pop_total=gdf_population,
                            pop_accessible=output_low,
                            population_column='pop')
                print(f"{city}: {sdg_low} percent of the population have access to low-capacity public transit systems")
            else:
                print(f"Low-capacity public transit stops of {city} do not exist")

            if  os.path.exists(pn + f'/{city}_Railstops.shp') and os.path.exists(pn + f'/{city}_Ferrystops.shp'):
                print("Both railway and ferry stops exist")
                df_railstops = gpd.read_file(pn + f'/{city}_Railstops.shp')
                df_rail_stops = df_railstops.to_crs('EPSG:4326').copy()
                stops_high_capacity = df_rail_stops
                df_ferrystops = gpd.read_file(pn + f'/{city}_Ferrystops.shp')
                df_ferry_stops = df_ferrystops.to_crs('EPSG:4326').copy()
                stops_high_capacity = df_ferry_stops
                stops_high_capacity = pd.concat([df_rail_stops, df_ferry_stops])

                stops_high_capacity_clip = gpd.clip(stops_high_capacity, boundary).copy()
                stops_high_capacity_clip.to_file(pn + f"/{city}_high_capacity_stops.gpkg", driver="GPKG")
                stops_high_capacity_clip = gpd.read_file(pn + f"/{city}_high_capacity_stops.gpkg").copy()

                print("Calculating accessibility to high-capacity public transit systems ...")
                accessibility_output_high = accessibility.distance_to_closest(
                start_geometries=gdf_population,
                destination_geometries=stops_high_capacity_clip,
                boundary_geometries=boundary,
                network_gdf=network,
                number_of_threads=4,
                transport_system="high-capacity",
                verbose=1)
                #print(f"accessibility calculated for {city} high-capacity transit system")

                #start_sdg = process_time()
                accessibility_output_high.to_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg", driver="GPKG")
                output_high = gpd.read_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg")

            elif os.path.exists(pn + f'/{city}_Railstops.shp') or os.path.exists(pn + f'/{city}_Ferrystops.shp'):
                print("Either railway or ferry stops exist")
                if os.path.exists(pn + f'/{city}_Railstops.shp'):
                    df_railstops = gpd.read_file(pn + f'/{city}_Railstops.shp')
                    df_rail_stops = df_railstops.to_crs('EPSG:4326').copy()
                    stops_high_capacity = df_rail_stops
                if os.path.exists(pn + f'/{city}_Ferrystops.shp'):
                    df_ferrystops = gpd.read_file(pn + f'/{city}_Ferrystops.shp')
                    df_ferry_stops = df_ferrystops.to_crs('EPSG:4326').copy()
                    stops_high_capacity = df_ferry_stops

                stops_high_capacity_clip = gpd.clip(stops_high_capacity, boundary).copy()
                stops_high_capacity_clip.to_file(pn + f"/{city}_high_capacity_stops.gpkg", driver="GPKG")
                stops_high_capacity_clip = gpd.read_file(pn + f"/{city}_high_capacity_stops.gpkg").copy()

                print("Calculating accessibility to high-capacity public transit systems ...")
                accessibility_output_high = accessibility.distance_to_closest(
                start_geometries=gdf_population,
                destination_geometries=stops_high_capacity_clip,
                boundary_geometries=boundary,
                network_gdf=network,
                number_of_threads=4,
                transport_system="high-capacity",
                verbose=1)
                #print(f"accessibility calculated for {city} high-capacity transit system")

                accessibility_output_high.to_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg", driver="GPKG")
                output_high = gpd.read_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg")
                sdg_high = accessibility.calculate_sdg(df_pop_total=gdf_population,
                             pop_accessible=output_high,
                             population_column='pop')
                # print(f"{city}: {sdg_high} percent of the population have access to high-capacity public transit systems")
                
            if not (output_low.empty and output_high.empty):
                sdg_low_high = accessibility.calculate_sdg(df_pop_total=gdf_population,
                                       pop_accessible=[output_low, output_high],
                                       population_column='pop')
                print(f"{city}: {sdg_low_high} percent of the population have access to low- and high-capacity public transit systems")
                print(f"SDG 11.2. indicator of {city}: {sdg_low_high}")
            elif not (output_low.empty or output_high.empty):
                if exists(output_low): 
                    print(f"High-capacity public transit stops of {city} do not exist")
                    print(f"SDG 11.2. indicator of {city}: {sdg_low}")
                else:
                    print(f"Low-capacity public transit stops of {city} do not exist")
                    print(f"SDG 11.2. indicator of {city}: {sdg_high}")
            else:
                print(f"Public transit stops of {city} do not exist") 
print("done")

