import psycopg2
conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
cur = conn.cursor()

query = "SELECT id FROM blog_distances"                                    
cur.execute(query)
distance_ids = cur.fetchall()

# 1 Unit is approximately 60 km

for i in range(len(distance_ids) ):
    distanceid=distance_ids[i][0]

    query = "SELECT id, ST_MemSize(geom) FROM blog_boundaries WHERE id NOT IN (SELECT boundary_id_id FROM blog_bufferzones WHERE distance_id_id=%d) order by ST_MemSize(geom)"%(distance_ids[i][0])                                      
    cur.execute(query)
    boundary_ids = cur.fetchall()
    for j in range(len(boundary_ids)):
        print('boundary ID:', boundary_ids[j][0], ',distance ID:' ,distance_ids[i][0], ',size:',boundary_ids[j][1])

        v = cur.execute("""
        INSERT INTO blog_bufferzones(distance_id_id, boundary_id_id, geom) 
        SELECT blog_distances.id, blog_boundaries.id, st_transform(ST_Buffer(st_simplify( st_transform(geom,27700),0.0001),
            distance * (CASE blog_distances.km_or_mile WHEN 'km' THEN 1000.0 ELSE 1609.344 END)), 4326)
        FROM blog_boundaries, blog_distances
        WHERE blog_boundaries.id = %d AND blog_distances.id = %d 
         """%(boundary_ids[j][0],distanceid))
        conn.commit()

        print('boundary ID:', boundary_ids[j][0], ', distance ID:' ,distance_ids[i][0], " completed" )
        

