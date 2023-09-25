import pandas as pd
import numpy as np
import networkx as nx
import osmnx as ox
import folium
import webbrowser as wb
'''ox.settings.log_console=True
ox.settings.use_cache=True'''

# Reads csv file and puts it in a Numpy array
csv_reader = pd.read_csv('DAA Prototype\\Parcels.csv')
parcels = np.array(csv_reader)

# Represents the 2 package group
group1 = []
group2 = []

# Separates packages according to their group
# id O000 represents the hub
for i in parcels:
    if(i[2].__contains__('A')):
        group1.append(i)
    elif (i[2].__contains__('B')):
        group2.append(i)
    else:
        group1.append(i)
        group2.append(i)

print("\n\nParcel Group 1")
print("Parcel ID\tWeight\t\tPrice")
for i in group1:
    
    print(f"{i[2]:<9}\t{i[3]:<9}\t{i[4]:<9}")

print("\n\nParcel Group2")
print("Parcel ID\tWeight\t\tPrice")
for i in group2:
    
    print(f"{i[2]:<9}\t{i[3]:<9}\t{i[4]:<9}")


#Knapsack Problem Algorithm
def knapsack(packages, max_weight):
    num_packages = len(packages)
    dp = [[0.0] * (max_weight + 1) for _ in range(num_packages + 1)]
    rider = [] # List to store selected packages

    # Dynamic programming loop to fill the DP table
    for i in range(1, num_packages + 1):
        for j in range(1, max_weight + 1):
            weight = packages[i - 1][3] # Weight of current package
            price = packages[i - 1][4]  # Price of current package
            
            # Check if current package can be included in the knapsack
            if weight <= j:
                # If current package is included, update the maximum price
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - weight] + price)
            else:
                # If current package cannot be included, use the previous row's value
                dp[i][j] = dp[i - 1][j]

    i = num_packages
    j = max_weight

    # Trace back to find the selected packages
    while i > 0 and j > 0:
        if dp[i][j] != dp[i - 1][j]:
            package = packages[i - 1] # Get the selected package
            rider.append(package) # Append selected package to the rider list
            j -= package[3] # Decrease the remaining weight
        i -= 1
    
    rider.append(packages[0][:])

    return rider

# Traveling Salesman Problem Algorithm
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

# Creating an adjacency matrix for TSP
def calculate_shortest_path(coordinates, graph):

    # Initialize the adjacency matrix
    num_packages = len(coordinates)
    adj_mat = [[0] * num_packages for _ in range(num_packages)]
    paths_addr = [[0] * num_packages for _ in range(num_packages)]
    

    # Calculate the distances and shortest paths between each pair of coordinates
    for i in range(num_packages):
        for j in range(num_packages):
            
            orig_node = ox.distance.nearest_nodes(graph, coordinates[i][1], coordinates[i][0])
            dest_node = ox.distance.nearest_nodes(graph, coordinates[j][1], coordinates[j][0])

            shortest_route = nx.shortest_path(graph, orig_node, dest_node, weight='length')
            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')

            # one by one
            adj_mat[i][j] = route_length
            paths_addr[i][j] = shortest_route

    return adj_mat, paths_addr


# Create a graph from OpenStreetMap within the boundaries of the given place
place = "Sampaloc, Fourth District, Manila, Capital District, Metro Manila, Philippines"
graph = ox.graph_from_place(place, network_type='all_private')
view = folium.Map(location=[14.6110, 120.9962], zoom_start=16)
paths1 = []
paths2 = []
for i in range(2):
    if i == 0:
        rider1 = knapsack(group1, 15000)
        rider = rider1
        adj_mat, paths_addr = calculate_shortest_path(rider1, graph)
    else:
        rider2 = knapsack(group2, 15000)
        rider = rider2
        adj_mat, paths_addr = calculate_shortest_path(rider2, graph)

    total_weight = 0; total_price = 0
    print(f"\n\nRider {i+1}")
    print("Parcel ID\tWeight\t\tPrice")
    for x in rider:
        print(f"{x[2]:<9}\t{x[3]/100:<9}\t{x[4]/100:<9}")
        total_weight += x[3]/100
        total_price += x[4]/100

    shortest_distance, shortest_path = 0, 0
    shortest_distance, shortest_path = tsp_held_karp(adj_mat)

    # When the shortest path returns to the original starting node
    shortest_path.append(0)
    shortest_distance += adj_mat[shortest_path[-2]][0]

    sum = 0
    print("\n\nDistances")
    for j in range(len(shortest_path) - 1):
        current_node = shortest_path[j]
        next_node = shortest_path[j + 1]
        print("Edge:", rider[current_node][2], "->", rider[next_node][2], "Distance:", adj_mat[current_node][next_node])
        sum = sum + adj_mat[current_node][next_node]

        #takes the path for tsp
        if i == 0:
            paths1.append(paths_addr[current_node][next_node])
        else:
            paths2.append(paths_addr[current_node][next_node])
    # Total sum of the shortest path
    print("\nThe Shortest Path Distance:",sum)

# Iterate over the coordinates and add markers with tooltips
for i, info in enumerate(rider1):
    if info[2] == 'O000':
        name = "Hub"
    else:
        stop_number = shortest_path.index(i) 
        name = f"Stop {stop_number}"

    marker = folium.Marker(location=(info[0],info[1]), popup=f"Coordinates: {info[0]}, {info[1]}")
    # Add tooltip with the name of the coordinate
    tooltip = folium.Tooltip(text=name)
    marker.add_child(tooltip)

    marker.add_to(view)

for i, info in enumerate(rider2):
    if info[2] == 'O000':
        name = "Hub"
    else:
        stop_number = shortest_path.index(i) 
        name = f"Stop {stop_number}"

    marker = folium.Marker(location=(info[0],info[1]), popup=f"Coordinates: {info[0]}, {info[1]}")
    # Add tooltip with the name of the coordinate
    tooltip = folium.Tooltip(text=name)
    marker.add_child(tooltip)

    marker.add_to(view)


# paths1 is rider1
for path in paths1: 
    #will convert the node ID into coordinates
    route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path]
    #plots the roads
    folium.PolyLine(locations=route_coordinates, color='red', weight=6).add_to(view)

# paths2 is rider2
for path in paths2: 
    #will convert the node ID into coordinates
    route_coordinates = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path]
    #plots the roads
    folium.PolyLine(locations=route_coordinates, color='blue', weight=6).add_to(view)

#browser kasi gamit so need isave nung folium file---pachange nalang ng directory
view.save(r'DAA Prototype\\mapping.html')
#opens file
wb.open(r'DAA Prototype\\mapping.html')
