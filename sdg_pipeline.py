import os
import sys
from time import process_time

import geopandas as gpd
import pandas as pd

from ptac import accessibility as accessibility
from ptac import osm as osm
from ptac import population as population

# Read path, name of directories and files located in 'data' path:
for path, dirnames, filenames in os.walk('data'):
    for city in dirnames:
        if not city.startswith('.'):
            pn = os.path.join(path, city)

            # check if boundary file exists:
            if os.path.exists(pn + f'/{city}_Boundary.shp'):
                # Read boundary shapefile:
                print(f"Reading city boundary of {city}...")
                gdf_place = gpd.read_file(pn + f"/{city}_Boundary.shp")
                boundary_gdf_place = gdf_place.to_crs('EPSG:4326').copy()
                # Save boundary data as a geopackage:
                boundary_gdf_place.to_file(pn + f"/{city}_Boundary.gpkg", driver="GPKG")
                # Read boundary geopackage:
                boundary = gpd.read_file(pn + f"/{city}_Boundary.gpkg")

                # Download street network from OSM:
                print(f"Downloading street network of {city} ...")
                network_gdf_place = osm.get_network(boundary).copy()
                # Save network data as a geopackage:
                network_gdf_place.to_file(pn + f"/{city}_network.gpkg", driver="GPKG")
                # Read network data:
                network = gpd.read_file(pn + f"/{city}_network.gpkg")
                print(f"Street network of {city} is downloaded.")
            
            # if boundary data does not exist, throw an error message and stop the process:
            else:
                print(f'File {city} boundary not found. Check the name of file.')
                break

            # check if population raster exists:
            if os.path.exists(pn + f'/{city}_Population.tif'):
                # Convert population raster to population points:    
                print(f"Converting population raster of {city} to population points ...")
                population_points = population.raster_to_points(pn + f"/{city}_Population.tif")  
                population_points = population_points[population_points['pop']>0]
                population_points['pop'] = population_points['pop']/ 1000
                # Clip population points with boundary and save as geopackage:
                population_points_clip = gpd.clip(population_points, boundary_gdf_place).copy()
                population_points_clip.to_file(pn + f"/{city}_pop_points_clip_10m.gpkg", driver="GPKG")
                gdf_population = gpd.read_file(pn + f"/{city}_pop_points_clip_10m.gpkg")
            
            # if population data does not exist, throw an error message and stop the process: 
            else:
                print(f'File {city} population not found. Check the name of file.')
                break

            # check if bus stops exist:
            if os.path.exists(pn + f'/{city}_Busstops.shp'):

                # Read and save public transport stops:
                print(f"Reading bus stops of {city}...")
                df_bustops = gpd.read_file(pn + f"/{city}_Busstops.shp")
                stops_low_capacity = df_bustops.to_crs('EPSG:4326').copy()
                stops_low_capacity_clip = gpd.clip(stops_low_capacity, boundary).copy()
                stops_low_capacity_clip.to_file(pn + f"/{city}_low_capacity_stops.gpkg", driver="GPKG")
                stops_low_capacity_clip = gpd.read_file(pn + f"/{city}_low_capacity_stops.gpkg").copy()

                # Calculate accessibilities for low-capacity transit systems:
                print("Calculating accessibility to low-capacity public transit systems ...")
                accessibility_output_low = accessibility.distance_to_closest(
                                            start_geometries=gdf_population,
                                            destination_geometries=stops_low_capacity_clip,
                                            boundary_geometries=boundary,
                                            network_gdf=network,
                                            number_of_threads=4,
                                            transport_system="low-capacity",
                                            verbose=1)

                # Save accessibility output of low-capacity pt systems as a geopackage:
                accessibility_output_low.to_file(pn + f"/{city}_output_low_capacity_without_gtfs.gpkg", driver="GPKG")
                output_low = gpd.read_file(pn + f"/{city}_output_low_capacity_without_gtfs.gpkg")
                sdg_low = accessibility.calculate_sdg(df_pop_total=gdf_population,
                            pop_accessible=output_low,
                            population_column='pop')
                print(f"{city}: {sdg_low} percent of the population have access to low-capacity public transit systems")
            else:
                print(f"Low-capacity public transit stops of {city} do not exist")

            # check if both railway stops and ferry stops exist:
            if  os.path.exists(pn + f'/{city}_Railstops.shp') and os.path.exists(pn + f'/{city}_Ferrystops.shp'):
                print("Both railway and ferry stops exist")

                # read railway and ferry stops:
                df_railstops = gpd.read_file(pn + f'/{city}_Railstops.shp')
                df_rail_stops = df_railstops.to_crs('EPSG:4326').copy()
                stops_high_capacity = df_rail_stops
                df_ferrystops = gpd.read_file(pn + f'/{city}_Ferrystops.shp')
                df_ferry_stops = df_ferrystops.to_crs('EPSG:4326').copy()
                stops_high_capacity = df_ferry_stops

                # combine both high-capacity public transit systems:
                stops_high_capacity = pd.concat([df_rail_stops, df_ferry_stops])

                # clip high-capacity pt systems with boundary:
                stops_high_capacity_clip = gpd.clip(stops_high_capacity, boundary).copy()

                # save clipped high-capacity pt systems as a geopackage:
                stops_high_capacity_clip.to_file(pn + f"/{city}_high_capacity_stops.gpkg", driver="GPKG")
                stops_high_capacity_clip = gpd.read_file(pn + f"/{city}_high_capacity_stops.gpkg").copy()

                # calculate accessibilities for high-capacity transit systems:
                print("Calculating accessibility to high-capacity public transit systems ...")
                accessibility_output_high = accessibility.distance_to_closest(
                start_geometries=gdf_population,
                destination_geometries=stops_high_capacity_clip,
                boundary_geometries=boundary,
                network_gdf=network,
                number_of_threads=4,
                transport_system="high-capacity",
                verbose=1)

                # save accessibility output of high-capacity pt sytsems as a geopackage:
                accessibility_output_high.to_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg", driver="GPKG")
                output_high = gpd.read_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg")

            # check if either of railway stops or ferry stops exist:
            elif os.path.exists(pn + f'/{city}_Railstops.shp') or os.path.exists(pn + f'/{city}_Ferrystops.shp'):
                print("Either railway or ferry stops exist")

                # check if rail stops exist:
                if os.path.exists(pn + f'/{city}_Railstops.shp'):
                    df_railstops = gpd.read_file(pn + f'/{city}_Railstops.shp')
                    df_rail_stops = df_railstops.to_crs('EPSG:4326').copy()
                    stops_high_capacity = df_rail_stops
                
                # check if ferry stops exist:
                if os.path.exists(pn + f'/{city}_Ferrystops.shp'):
                    df_ferrystops = gpd.read_file(pn + f'/{city}_Ferrystops.shp')
                    df_ferry_stops = df_ferrystops.to_crs('EPSG:4326').copy()
                    stops_high_capacity = df_ferry_stops

                # clip high-capacity pt system with boundary geometry:
                stops_high_capacity_clip = gpd.clip(stops_high_capacity, boundary).copy()

                # save clipped high-capacity pt system as a geopackage:
                stops_high_capacity_clip.to_file(pn + f"/{city}_high_capacity_stops.gpkg", driver="GPKG")
                stops_high_capacity_clip = gpd.read_file(pn + f"/{city}_high_capacity_stops.gpkg").copy()

                # calculate accessibilities for high-capacity transit systems:
                print("Calculating accessibility to high-capacity public transit systems ...")
                accessibility_output_high = accessibility.distance_to_closest(
                start_geometries=gdf_population,
                destination_geometries=stops_high_capacity_clip,
                boundary_geometries=boundary,
                network_gdf=network,
                number_of_threads=4,
                transport_system="high-capacity",
                verbose=1)

                # save accessibility output of high-capacity pt systems as a geopackage:
                accessibility_output_high.to_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg", driver="GPKG")
                output_high = gpd.read_file(pn + f"/{city}_output_high_capacity_without_gtfs.gpkg")

                # calculate SDG 11.2.1 indicator for high-capacity pt systems:
                sdg_high = accessibility.calculate_sdg(df_pop_total=gdf_population,
                             pop_accessible=output_high,
                             population_column='pop')
                # print(f"{city}: {sdg_high} percent of the population have access to high-capacity public transit systems")
            
            # check if accesibilities of both low- and high-capacity pt systems exist: 
            if not (output_low.empty and output_high.empty):
                sdg_low_high = accessibility.calculate_sdg(df_pop_total=gdf_population,
                                       pop_accessible=[output_low, output_high],
                                       population_column='pop')
                print(f"{city}: {sdg_low_high} percent of the population have access to low- and high-capacity public transit systems")
                print(f"SDG 11.2. indicator of {city}: {sdg_low_high}")

            # check if accesibilities of either low- or high-capacity pt systems do not exist:
            elif not (output_low.empty or output_high.empty):

                # calculate SDG 11.2.1 indicator based on low-capacity pt systems:
                if exists(output_low): 
                    print(f"High-capacity public transit stops of {city} do not exist")
                    print(f"SDG 11.2. indicator of {city}: {sdg_low}")
                
                # calculate SDG 11.2.1 indicator based on high-capacity pt systems:
                else:
                    print(f"Low-capacity public transit stops of {city} do not exist")
                    print(f"SDG 11.2. indicator of {city}: {sdg_high}")
            
            # if there is no public transit stops, print an error message:
            else:
                print(f"Public transit stops of {city} do not exist")
                break
print("Process completed! ")

