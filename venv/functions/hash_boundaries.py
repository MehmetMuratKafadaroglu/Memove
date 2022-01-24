import psycopg2
import json

def boundaries():
    con = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = con.cursor()
    query = "SELECT search_name, borough, county FROM blog_boundaries"
    cur.execute(query)
    results = cur.fetchall()
    search_names = []

    for result in results:
        name = result[0]
        borough = result[1]
        county = result[2]
        if borough is not None:
            borough = borough.replace("(B)", "")
            borough = borough.replace("District", "")
            borough = borough.replace("  ,", " ,")
            borough = borough.replace("  ", " ")

            name += "("
            name += borough + ","
            if county is None:
                 name = name[:-1]
            else:
                name += county
            name += ")"
        name = name.replace("Greater London", "London")
        search_names.append(name)

    f = open("../memove/blog/static/js/find_distance.js", "w")
    values = json.dumps(search_names)
    f.write(values)
    f.close()


def universities():
    con = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = con.cursor()
    query = "SELECT search_name FROM blog_boundaries WHERE type='University'"
    cur.execute(query)
    results = cur.fetchall()
    search_names = []

    for result in results:
        name = result[0]
        fin = "{}".format(name)
        search_names.append(fin)

    f = open("../memove/blog/static/js/universities.js", "w")
    values = json.dumps(search_names)
    f.write(values)
    f.close()

universities()