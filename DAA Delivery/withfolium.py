import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import numpy as np
import folium
import webbrowser as wb


# define the start and end locations in latlng
start_latlng = (14.5861,121.0318)
end_latlng = (14.5867,121.0529)
# location where you want to find your route
place     = "Mandaluyong, Eastern Manila District, Metro Manila, Philippines"
# find shortest route based on the mode of travel
mode      = 'all_private'        # 'drive', 'bike', 'walk'
# find shortest path based on distance or time
optimizer = 'length'        # 'length','time'
# create graph from OSM within the boundaries of some 
# geocodable place(s)
graph = ox.graph_from_place(place, network_type = mode)

orig_node = ox.distance.nearest_nodes(graph, start_latlng[1],
                                      start_latlng[0])
dest_node = ox.distance.nearest_nodes(graph, end_latlng[1],
                                      end_latlng[0])
shortest_route = nx.shortest_path(graph, 
                                  orig_node, 
                                  dest_node, 
                                  weight='length')

route_length = nx.shortest_path_length(graph, 
                                  orig_node, 
                                  dest_node, 
                                  weight='length')

view = folium.Map(location=[14.6110, 120.9962], zoom_start=13)
route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_route]
folium.PolyLine(locations=route_coordinates, color='red', weight=6).add_to(view)
view.save(r'DAA Delivery\\mapping.html')
wb.open(r'DAA Delivery\\mapping.html')