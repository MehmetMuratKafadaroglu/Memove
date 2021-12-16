import psycopg2
conn = psycopg2.connect("dbname='test' user='postgres' host='localhost' password='630991'")
cur = conn.cursor()

def gps_cordinates_to_lat_lon(cordinates):
    string = str(cordinates)
    coords = string.split()
    latitude = float(coords[0].replace('Â°N', '').replace("('", "").replace(")'", ""))
    longitude = float(coords[1].replace('Â°E', '').replace('Â°W','').replace("('", "").replace("',)", ""))
    
    if 'E' in coords[1]:
        longitude = longitude * (-1)
    if 'S' in coords[0]:
        raise ValueError('The given cordinates cannot be true')
    
    return latitude, longitude

for i in range(2, 370):
    cur.execute("SELECT coordinates FROM london_overground_stations WHERE id=%d"%(i))
    cordinate = cur.fetchone()
    cordinates = gps_cordinates_to_lat_lon(cordinate)
    print(cordinates[0], cordinates[1])
    data =  (cordinates[0], cordinates[1], i) 
    cur.execute("UPDATE london_overground_stations SET latitude = %s, longitude = %s WHERE id = %s ;" , data)
    
    conn.commit()