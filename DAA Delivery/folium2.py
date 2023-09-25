import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import folium
import webbrowser as wb


coordinates = [
    (14.603186410693931, 120.99234620494717), #Hub coordinate
    (14.603364127623895, 120.99685799482054),
    (14.608592390002121, 120.9972169550424),
    (14.603666736742872, 121.00381613817692),
    (14.608656098204063, 120.99411551128767),
    (14.610618283405064, 120.99633452352917),
    (14.61107998957333, 120.99865079572137),
    (14.603443669741392, 120.98795583761674),
    (14.607311771350856, 121.00514573002489),
    (14.607074447854824, 121.0014881037439),
    (14.607853177762541, 121.00070006328447),
    (14.609125946584378, 120.99954220349703),
    (14.610009709331838, 121.00018928642093),
    (14.609332193469095, 121.00096538397526),
    (14.609830688280478, 121.00595100428899),
    (14.610395037103046, 121.00524831095635),
    (14.614061252667776, 121.0007436745257)
    
]

# location where you want to find your route
place = "Sampaloc, Fourth District, Manila, Capital District, Metro Manila, Philippines"
# find shortest route based on the mode of travel
mode = 'all_private'        # 'drive', 'bike', 'walk'
# find shortest path based on distance or time
optimizer = 'length'        # 'length','time'
# create graph from OSM within the boundaries of some geocodable place(s)
graph = ox.graph_from_place(place, network_type = mode)


# Initialize the adjacency matrix
adj_mat = [[0] * len(coordinates) for _ in range(len(coordinates))]

#matrix for paths
paths_addr = [[0] * len(coordinates) for _ in range(len(coordinates))]

#1d array container for tsp path
paths = []


#calculates the distance of a node to other nodes (shortest path)
for i in range(len(coordinates)):
    for j in range(len(coordinates)):
        if i >= j: #to avoid redundancy in calculation (i and j = j and i) 

            orig_node = ox.distance.nearest_nodes(graph, coordinates[i][1], coordinates[i][0])
            dest_node = ox.distance.nearest_nodes(graph, coordinates[j][1], coordinates[j][0])

            #finds the roads or edges to be takes
            shortest_route = nx.shortest_path(graph, orig_node, dest_node, weight='length')
            #calculates the length of the path
            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')
            
            if route_length != 0: #this indicate that the path is valid
                print(f"The network distance between the two coordinates is: {route_length} meters")
            
            #creates an adjacency matrix
            adj_mat[i][j] = route_length
            adj_mat[j][i] = route_length
            paths_addr[i][j] = shortest_route
            paths_addr[j][i] = shortest_route

# Optimized solution
def tsp_held_karp(distances):
    num_nodes = len(distances)
    memo = {}

    def tsp_util(current_node, remaining_nodes):
        if len(remaining_nodes) == 0:
            return distances[current_node][0], [current_node]  # Return distance and path to the starting node

        if (current_node, tuple(remaining_nodes)) in memo:
            return memo[(current_node, tuple(remaining_nodes))]

        min_distance = float('inf')
        min_path = []
        for next_node in remaining_nodes:
            new_remaining_nodes = list(remaining_nodes)
            new_remaining_nodes.remove(next_node)
            distance, path = tsp_util(next_node, tuple(new_remaining_nodes))
            total_distance = distances[current_node][next_node] + distance
            if total_distance < min_distance:
                min_distance = total_distance
                min_path = [current_node] + path

        memo[(current_node, tuple(remaining_nodes))] = (min_distance, min_path)
        return min_distance, min_path

    return tsp_util(0, tuple(range(1, num_nodes)))

# Distances represented as a 2D matrix
distances = adj_mat

# Calculate the shortest TSP tour
shortest_distance, shortest_path = tsp_held_karp(distances)

# When the shortest path returns to the original starting node
shortest_path.append(0)
shortest_distance += distances[shortest_path[-2]][0]

# Print the path taken for each edge in the tour
print("Shortest TSP tour path per Node:")

sum = 0
for i in range(len(shortest_path) - 1):
    current_node = shortest_path[i]
    next_node = shortest_path[i + 1]
    print("Edge:", current_node, "->", next_node, "Distance:", distances[current_node][next_node])
    sum = sum + distances[current_node][next_node]

    # Takes the path for tsp
    paths.append(paths_addr[current_node][next_node])

# Total sum of the shortest path
print("\nThe Shortest Path Distance:",sum)

# Creates the folium map
view = folium.Map(location=[14.608784, 120.996147], zoom_start=16)


# Iterate over the coordinates and add markers with tooltips
for i, (lat, lon) in enumerate(coordinates):
    if i == 0:
        name = "Hub"
    else:
        stop_number = shortest_path.index(i) 
        name = f"Stop {stop_number}"

    marker = folium.Marker(location=(lat, lon), popup=f"Coordinates: {lat}, {lon}")

    # Add tooltip with the name of the coordinate
    tooltip = folium.Tooltip(text=name)
    marker.add_child(tooltip)

    marker.add_to(view)

for path in paths:
    route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path]
    folium.PolyLine(locations=route_coordinates, color='blue', weight=6).add_to(view)


# To save and open the generated map as html 
view.save(r'DAA Delivery\\mapping.html')
wb.open(r'DAA Delivery\\mapping.html')