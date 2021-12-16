import psycopg2

conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
cur = conn.cursor()
query = "SELECT id FROM blog_postcodes"         
cur.execute(query)
postcode_ids = cur.fetchall()

for i in range(len(postcode_ids)):
    postcode_id=postcode_ids[i][0]
    cur.execute("DELETE FROM blog_nearestrailwaystations WHERE postcode_id = %d"%(postcode_id))
    print(postcode_id)
    cur.execute("""
    INSERT INTO blog_nearestschools(distance, boundary_id, postcode_id)
    SELECT 
    ST_Distance(ST_Transform(geom,27700),ST_Transform(ST_SetSRID( ST_Point(longitude , latitude)::geometry, 4326),27700)),
    blog_boundaries.id,
    blog_postcodes.id
    FROM blog_boundaries, blog_postcodes
    WHERE type='School' and blog_postcodes.id=%d 
    ORDER BY ST_Distance(ST_Transform(geom,27700),ST_Transform(ST_SetSRID( ST_Point(longitude , latitude)::geometry, 4326),27700)) 
    LIMIT 3;"""%(postcode_id))
    conn.commit()
    print(postcode_id, 'completed')


conn.close()
