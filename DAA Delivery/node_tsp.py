import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import numpy as np


coordinates = [
    (14.6207,120.9993), #1
    (14.6237,120.9908), #2
    (14.6205,120.9941), #3
    (14.6187,120.9928), #4
    (14.6162,120.9911), #5
    (14.6150,120.9920), #6
    (14.6170,120.9943)  #7
    # ... add more coordinates here
]

# location where you want to find your route
place = "Sampaloc, Fourth District, Manila, Capital District, Metro Manila, Philippines"
# find shortest route based on the mode of travel
mode = 'all_private'        # 'drive', 'bike', 'walk'
# find shortest path based on distance or time
optimizer = 'length'        # 'length','time'
# create graph from OSM within the boundaries of some 
# geocodable place(s)
graph = ox.graph_from_place(place, network_type = mode)

'''fig, ax = ox.plot_graph(graph)'''

# Initialize the adjacency matrix
adj_mat = [[0] * len(coordinates) for _ in range(len(coordinates))]

#matrix for paths
paths_addr = [[0] * len(coordinates) for _ in range(len(coordinates))]

#1d array na paglalagyan nung tsp path
paths = []


#calculates the distance of a node to other nodes (shortest path)
for i in range(len(coordinates)):
    for j in range(len(coordinates)):
        if i >= j:
            orig_node = ox.distance.nearest_nodes(graph, coordinates[i][1], coordinates[i][0])
            dest_node = ox.distance.nearest_nodes(graph, coordinates[j][1], coordinates[j][0])

            #finds the roads or edges to be takes
            shortest_route = nx.shortest_path(graph, orig_node, dest_node, weight='length')
            #calculates the length of the path
            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')
            
            if route_length != 0:
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

    #takes the path for tsp
    paths.append(paths_addr[current_node][next_node])

# Total sum of the shortest path
print("\nThe Shortest Path Distance:",sum)

# plot_graph_routes --- if isa lang na path plot_graph_route walang 's'
ox.plot_graph_routes(graph, paths, route_linewidth=6, node_size=0, route_color='green')