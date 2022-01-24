import psycopg2

def put_to_array(fetch_results):
    results = []

    for result in fetch_results:
        results.append(result[0])

    return results
def get_station_ids():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()

    query= "SELECT id FROM blog_stations ;"
    cur.execute(query)
    conn.commit()
    values= cur.fetchall()
    values = put_to_array(values)
    return  values

def is_same_line(*args):
    values =  []
    for id in args:
        conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
        cur = conn.cursor()
        query= "SELECT line_id FROM blog_stations WHERE id=%s;"
        cur.execute(query, [id])
        conn.commit()
        value = cur.fetchone()

        if value is None:
            return False

        else:
            value = value[0]
        values.append(value)

    for val in values:
        if val != values[0]:
            return False
    return True


def get_possible_routes(origin):
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query= "SELECT destination FROM blog_times WHERE origin=%s;"
    cur.execute(query, [origin])
    conn.commit()
    value = cur.fetchall()
    conn.close()
    return value

def make_edge(origin):
    possible_routes = get_possible_routes(origin)
    possible_routes = put_to_array(possible_routes)
    edge = {origin: possible_routes}
    return edge

def get_key(dicti):
    keys = []
    for key in dicti.keys():
        keys.append(key)
    return key

def get_edges():
    ids = get_station_ids()
    edges = {}
    for id in ids:
        a = make_edge(id)
        key = get_key(a)
        values = a.get(key)
        edges[key] = values
        #print("added: ", a)
    print("Complited the Edges")
    return edges

def get_weights():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query= "SELECT origin, destination, duration FROM blog_times;"
    cur.execute(query)
    conn.commit()
    values = cur.fetchall()
    conn.close()

    weights = {}
    for value in values:
        tpl = (value[0], value[1])
        weights[tpl] = value[2]
        #print("added: ", "{",tpl,":", value[2], "}")
    print("Complited the Weights")
    return weights   

def time_takes(path):
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    duration = 0
    
    for i in range(0 ,len(path)-1):
        orig = path[i]
        dest = path[i+1]
        if type(path) is str:
            return None
        cur = conn.cursor()
        query= "SELECT duration FROM blog_times WHERE origin=%s AND destination=%s;"
        cur.execute(query, [orig, dest])
        conn.commit()
        durat = cur.fetchone()
        
        assert durat is not None
        durat = durat[0]

        duration += durat 
    return duration

class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = get_edges()
        self.weights = get_weights()
    
    def add_edge(self, from_node, to_node, weight):
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight


def dijsktra(graph, initial, end):
    # shortest paths is a dict of nodes
    # whose value is a tuple of (previous node, weight)
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    while current_node != end:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + weight_to_current_node
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route Not Possible"
        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
    # Work back through destinations in shortest path
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    # Reverse path
    path = path[::-1]
    return path

my_graph = Graph()
ids = get_station_ids()
for origin in ids:
    for destination in ids:
        path = dijsktra(my_graph, origin, destination)
        duration = time_takes(path)
        if duration is not None:
            conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
            cur = conn.cursor()

            query= "INSERT INTO blog_times(origin, destination, duration)VALUES(%s, %s, %s) ON CONFLICT DO NOTHING;"
            cur.execute(query, [origin, destination, duration])
            conn.commit()
            conn.close()
            print("Origin:", origin, "to: ", destination, "\n Duration: ",duration)


#319379