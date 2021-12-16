import os
import psycopg2

arr = os.listdir('C:\mapping\London Station Names')
untouched = arr
conn = psycopg2.connect("dbname='test' user='postgres' host='localhost' password='630991'")
cur = conn.cursor()

lines = [0,
'Bakerloo',
'Central',
'Circle',
'District',
'DLR',
'Hammersmith-City',
'London-Overground',
'Jubilee',
'Metropolitan',
'Northern',
'Piccadily',
'TFL',
'Tram',
'Victoria',
'Waterloo-City']


i = 0
while i < len(arr):
    splited_version = arr[i].split()
    name_of_the_line = splited_version[0]

    j = 1
    while j < len(lines):
        if name_of_the_line == lines[j]:
            my_line_id = j
            break

        else:
             j = j+1
    splited_version.pop(0)
    name_of_the_route = " ".join(splited_version)
    name_of_the_route = name_of_the_route.replace('.csv', ' ')
    print(my_line_id, name_of_the_route)
    
    
    query = """
        DELETE FROM trains_test;

        COPY trains_test
        FROM 'C:\mapping\London Station Names\%s'
        DELIMITER ',' 
        CSV HEADER;

        DROP TABLE trains_middle;

        CREATE TABLE trains_middle(
        id SERIAL,
        station_name VARCHAR(50),
        PRIMARY KEY(id)
        );

        INSERT INTO trains_middle(station_name)
        SELECT trains_test.name FROM trains_test;

        INSERT INTO trains_actual(station_name, station_order, route, line_id)
        SELECT trains_middle.station_name, trains_middle.id, '%s', %d FROM trains_middle  ;
    """%(untouched[i],name_of_the_route, my_line_id)
    print(my_line_id, name_of_the_route, "Finished")
    cur.execute(query)
    conn.commit()
    i = i + 1
        
    

