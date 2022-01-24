import os
import psycopg2
MAPS_PATH = "../memove/blog/static/maps/"

conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
cur = conn.cursor()
query = "SELECT id FROM blog_post"
cur.execute(query)
ids = cur.fetchall()

query = "SELECT id FROM blog_post ORDER BY id DESC LIMIT 1;"
cur.execute(query)
maxid = cur.fetchone()
maxid = maxid[0]

ids_copy = []
for pk in ids:
    pk = pk[0]
    ids_copy.append(pk)

for i in range(maxid + 100):
    if not i in ids_copy:
        file = MAPS_PATH + "%d.html" % i
        if os.path.isfile(file):
            os.remove(file)
