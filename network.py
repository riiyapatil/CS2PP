def file_to_edge_list(file_path, node):
    """returns the edges respective to the specified node

    Keyword arguments
    file_name(string) -- the file containing the data needed to be scanned
    node(integer) -- specified number to compare file data to
    """

    result = []
    
    with open(file_path, 'r') as file:
        for line in file:
                edge = tuple(map(int, line.strip().split('\t')))
                if node == "all":
                    result.append(edge)
                elif node in edge:
                    result.append(edge)
    return(result)
                
    """opening a file with a context manager"""

def edge_to_neighbour_list1(edge_list):
    """returns a neighbour list representation of the above processed edge list

    Keyword arguments
    edge_list(function) -- the file containing the data needed to be scanned
    """
    neighbor_dict = {}
    for u, v in edge_list:
        # Add v to u's neighbors
        if u not in neighbor_dict:
            neighbor_dict[u] = []
        neighbor_dict[u].append(v)
        
        # Add u to v's neighbors (for undirected edges)
        if v not in neighbor_dict:
            neighbor_dict[v] = []
        neighbor_dict[v].append(u)
    return neighbor_dict

def edge_to_neighbour_list2(edge_list):
    """Less efficient adjacency list (list of tuples)."""
    adjacency_list = []
    # Collect all unique nodes (inefficient for large datasets)
    nodes = set()
    for u, v in edge_list:
        nodes.add(u)
        nodes.add(v)
    # For each node, scan all edges to find neighbors (O(n×m))
    for node in nodes:
        neighbors = []
        for u, v in edge_list:
            if u == node:
                neighbors.append(v)
            if v == node:  # Assuming undirected edges
                neighbors.append(u)
        adjacency_list.append((node, neighbors))
    return adjacency_list

def inspect_node(network, node):
    """Return edges or neighbors for a node based on the network type.
    
    Keyword arguments:
    network (list or dict) -- Edge list or neighbor list.
    node (int) -- The node to inspect.
    """
    # Case 1: Edge list (list of tuples)
    if isinstance(network, list) and all(isinstance(e, tuple) for e in network):
        # Initialize empty list to store matching edges
        result = []
        
        # Check each edge for node membership
        for current_edge in network:
            if node in current_edge:
                result.append(current_edge)
        return result
    
    # Case 2: Neighbor list (dictionary)
    elif isinstance(network, dict):
        return network.get(node, [])
    
    # Case 3: Adjacency list (list of tuples)
    elif isinstance(network, list) and all(isinstance(e, tuple) and len(e) == 2 for e in network):
        for entry in network:
            current_node, neighbors = entry
            if current_node == node:
                return neighbors
        return []
    
    else:
        raise ValueError("Unsupported network type.")

def get_degree_statistics(neighbor_list):
    # Determine degrees based on the type of neighbor list
    if isinstance(neighbor_list, dict):
        degrees = [len(neighbors) for neighbors in neighbor_list.values()]
    else:
        degrees = [len(neighbors) for _, neighbors in neighbor_list]
    
    max_degree = max(degrees)
    min_degree = min(degrees)
    
    # Calculate average using a lambda function
    average_degree = (lambda d: sum(d) / len(d))(degrees)
    
    # Find the most common degree
    frequency = {}
    for degree in degrees:
        frequency[degree] = frequency.get(degree, 0) + 1
    max_count = max(frequency.values())
    most_common_degrees = [k for k, v in frequency.items() if v == max_count]
    most_common = most_common_degrees[0]  # Select the first most common degree
    
    return (max_degree, min_degree, average_degree, most_common)

def get_clustering_coefficient(*, network, node):
    """
    Calculate the clustering coefficient for a specified node.

    Keyword arguments:
    network (dict): Neighbor list representation of the graph.
    node (int): Node for which to calculate the clustering coefficient.
    
    Returns:
    float: The clustering coefficient of the node.
    """
    # Get the neighbors of the node
    neighbors = network.get(node, [])
    
    # If the node has fewer than 2 neighbors, the clustering coefficient is 0
    if len(neighbors) < 2:
        return 0.0

    # Count the actual edges among the neighbors
    actual_edges = 0
    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            # Check if neighbors[i] and neighbors[j] are connected
            if neighbors[j] in network.get(neighbors[i], []):
                actual_edges += 1

    # Calculate the maximum number of possible edges among neighbors
    max_edges = len(neighbors) * (len(neighbors) - 1) // 2

    # Calculate and return the clustering coefficient
    return actual_edges / max_edges
