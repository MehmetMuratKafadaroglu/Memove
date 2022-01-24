import psycopg2
from difflib import get_close_matches

def put_to_array(fetch_results):
    results = []

    for result in fetch_results:
        results.append(result[0])

    return results
def get_station_names():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()

    query= "SELECT station_name FROM blog_stations ;"
    cur.execute(query)
    conn.commit()
    values= cur.fetchall()
    values = put_to_array(values)
    return  values

def get_boundary_id(name):
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()

    query= "SELECT id FROM blog_boundaries WHERE name=%s AND type='Railway Station';"
    cur.execute(query, [name])
    conn.commit()
    
    values= cur.fetchone()
    values = values[0]
    return values


def detect_errors():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    cur.execute("SELECT boundary_id FROM blog_stations")
    ids = cur.fetchall()
    ids = put_to_array(ids)
    errors = []
    for id in ids:
        cur.execute("SELECT type FROM blog_boundaries WHERE id=%s",[id])
        boundary = cur.fetchone()
        boundary = boundary[0]

        if boundary != 'Railway Station':
            cur.execute("SELECT station_name FROM blog_stations WHERE id=%s", [id])
            station = cur.fetchall()
            station = put_to_array(station)
            if len(station):
                errors.append(station)
    conn.close()

    #if error length is 0
    if not len(errors):
        print("Errors did not occur")
    else:
        print(errors)


def get_station_names_in_london():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query="""
        SELECT name FROM blog_boundaries, blog_bufferzones 
        WHERE blog_boundaries.type='Railway Station' 
        AND blog_bufferzones.id=79908
        AND ST_contains(blog_bufferzones.geom, blog_boundaries.geom);
        """
    cur.execute(query)
    conn.commit()
    values= cur.fetchall()
    values = put_to_array(values)
    return values


names_from_statios = get_station_names()
boundaries = get_station_names_in_london()
unidentifiable_stations = []

for station in names_from_statios:
    closest_name = get_close_matches(station, boundaries)
    #If there are close names
    if len(closest_name):
        closest_name = closest_name[0]
        boundary_id = get_boundary_id(closest_name)
        conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
        cur = conn.cursor()
        query="UPDATE blog_stations SET boundary_id = %s WHERE station_name = %s ;"
        cur.execute(query, [boundary_id, station])
        conn.commit()
        conn.close()
        print("For %s closest name is %s"% (station, closest_name))
    #Close name could not find
    else:
        unidentifiable_stations.append(station)

copy = unidentifiable_stations

for station in unidentifiable_stations:
    i = 0.6
    # If a name is not found
    while i <= 1.0:
        closest_name = get_close_matches(station, boundaries, n=1, cutoff=i)
        if len(closest_name):
            closest_name = closest_name[0]
            boundary_id = get_boundary_id(closest_name)
            conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
            cur = conn.cursor()
            query = "UPDATE blog_stations SET boundary_id = %s WHERE station_name = %s;"
            cur.execute(query, [boundary_id, station])
            conn.commit()
            conn.close()
            print("For %s closest name is %s" % (station, closest_name))
            copy.remove(station)
            break
        i += 0.1

even_unidentified = {'Knightsbridge Underground Station': 'Knightsbridge Station',
                   'Oxford Circus Underground Station': 'Oxford Circus Station',
                   'Upney Station': 'Upney Station',
                    'Monument' : 'Monument Station',
                   'Victoria Station' : 'Victoria Station',
                    'Cutty Sark' : 'Cutty Sark for Maritime Greenwich Station',
                   'Chesham Underground Station' : 'Chesham Station',
                    'Belgrave Walk' : 'Belgrave Walk Station',
                   'Ampere Way' : 'Ampere Way Station',
                    "King Henry's Drive": 'King Henrys Drive Station',
                    'Fieldway' : 'Fieldway Station',
                   'Turkey Street Station': 'Turkey Street Station',
                    'Greenhithe for Bluewater': 'Greenhithe Station'}

for item in even_unidentified.items():
    stn = item[0]
    boundary = item[1]
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query = """UPDATE blog_stations SET boundary_id = 
    (SELECT id FROM blog_boundaries WHERE search_name= %s)
    WHERE station_name = %s
    """
    cur.execute(query, [boundary, stn])
    conn.commit()
    conn.close()

conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
cur = conn.cursor()
query = """SELECT station_name FROM blog_stations WHERE boundary_id is null
"""
cur.execute(query)
unidentified = cur.fetchall()
conn.commit()
conn.close()
print("Unidetified stations: ",unidentified)
detect_errors()