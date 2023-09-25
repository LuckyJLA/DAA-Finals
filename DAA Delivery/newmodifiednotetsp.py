import networkx as nx
import osmnx as ox

def calculate_shortest_path(coordinates):
    # Create a graph from OpenStreetMap within the boundaries of the given place
    place = "Sampaloc, Fourth District, Manila, Capital District, Metro Manila, Philippines"
    graph = ox.graph_from_place(place, network_type='all_private')

    # Initialize the adjacency matrix
    num_packages = len(coordinates)
    adj_mat = [[0] * num_packages for _ in range(num_packages)]
    paths_addr = [[0] * num_packages for _ in range(num_packages)]
    paths = []

    # Calculate the distances and shortest paths between each pair of coordinates
    for i in range(num_packages):
        for j in range(num_packages):
            if i >= j:
                orig_node = ox.distance.nearest_nodes(graph, coordinates[i][1], coordinates[i][0])
                dest_node = ox.distance.nearest_nodes(graph, coordinates[j][1], coordinates[j][0])

                shortest_route = nx.shortest_path(graph, orig_node, dest_node, weight='length')
                route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')

                adj_mat[i][j] = route_length
                adj_mat[j][i] = route_length
                paths_addr[i][j] = shortest_route
                paths_addr[j][i] = shortest_route

    # Optimized solution for the TSP
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

    distances = adj_mat
    shortest_distance, shortest_path = tsp_held_karp(distances)

    shortest_path.append(0)
    shortest_distance += distances[shortest_path[-2]][0]

    print("\nShortest TSP tour path per Node:")
    total_distance = 0
    for i in range(len(shortest_path) - 1):
        current_node = shortest_path[i]
        next_node = shortest_path[i + 1]
        print("Deliver Package", coordinates[current_node][2], "from", coordinates[current_node][:2],
              "to", coordinates[next_node][:2], "Distance:", distances[current_node][next_node], "meters")
        total_distance += distances[current_node][next_node]
        paths.append(paths_addr[current_node][next_node])

    print("\nThe Total Distance of the Shortest Path:", total_distance)

    return paths

# Example usage with a list of packages
packages = [
    (14.603186410693931, 120.99234620494717, 1, 500.5, 100),
    (14.603364127623895, 120.99685799482054, 2, 700, 150),
    (14.608592390002121, 120.9972169550424, 3, 1000, 200),
    (14.603666736742872, 121.00381613817692, 4, 900, 180),
    (14.608656098204063, 120.99411551128767, 5, 1200, 250),
    (14.610618283405064, 120.99633452352917, 6, 800, 120),
    (14.61107998957333, 120.99865079572137, 7, 600, 90),
    (14.603443669741392, 120.98795583761674, 8, 1000, 180),
    (14.607311771350856, 121.00514573002489, 9, 1100, 210),
    (14.607074447854824, 121.0014881037439, 10, 700, 120),
    (14.607853177762541, 121.00070006328447, 11, 1300, 230),
    (14.609125946584378, 120.99954220349703, 12, 900, 150),
    (14.610009709331838, 121.00018928642093, 13, 600, 100),
    (14.609332193469095, 121.00096538397526, 14, 800, 140),
    (14.609830688280478, 121.00595100428899, 15, 1200, 200),
    (14.610395037103046, 121.00524831095635, 16, 950, 160),
    (14.614061252667776, 121.0007436745257, 17, 2000, 300)
]

shortest_paths = calculate_shortest_path(packages)
