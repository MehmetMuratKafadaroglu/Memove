import os
import psycopg2

file = open('times.txt', 'r')
f = file.readlines()
number_of_lines = len(f)
final_array = []
line_names = []
carry_line_name = None


def is_this_a_line(product):
    if not product[0]:
        name = product[1].split(' ')
        if "to" in name:
            return True
    else:
        return False


def get_line_name(station):
    for product in final_array:
        if not product[0]:
            name = product[1].split(' ')
            if "to" in name:
                carry_line_name = name[0]
        if product[1]==station:
            return carry_line_name 


def is_station_in(line, station):
    line_station_in = get_line_name(station)
    if line_station_in == line:
        return True
    else:
        return False


def detect_errors(product, line_number):
    array_length = len(product)
    if array_length > 2 and product[2] != "This is a transfer" and product[0] < 0:
        print(product)
        print("In this line: %i" %line_number)
        raise ValueError("Array starts with - but array length is less than 3")
    if array_length > 2 and product[1] == product[2]:
        print(product)
        print("In this line: %i" %line_number)
        raise ValueError("Array's second and third element is same")
    if product[0] < 0:
        print(product)
        print("In this line: %i" %line_number)
        raise ValueError("This should not start with negative number")
    if type(product[0]) != type(1):
        print(product)
        print("In this line: %i" %line_number)
        raise ValueError("This should be integer")
    if product[0] > 0 and len(product) < 3:
        print(product)
        print("In this line: %i" %line_number)
        raise ValueError("Less than three array elements")


def insert_stations():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    for product in final_array:
        if is_this_a_line(product):
            current_line_name = product[1].split(' ')
            current_line_name = current_line_name[0]
        
        if not is_this_a_line(product):
            lin = current_line_name
            query = "SELECT id FROM blog_lines WHERE name=%s"
            
            cur = conn.cursor()
            cur.execute(query, [lin])
            conn.commit()
            line_id = cur.fetchone()
            
            assert line_id is not None
            
            line_id = line_id[0]

            #Insert the station name and id to the blog_stations table
            if product[0] > 0:
                station_name=product[1]
                station_name = station_name.strip()
                print("Inserting", station_name)
                query = "INSERT INTO blog_stations (line_id, station_name) VALUES(%s, %s) ON CONFLICT DO NOTHING"
                cur.execute(query, [line_id, station_name])
                conn.commit()
    conn.close()

def insert_times():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    for i in range(len(final_array)):
        product = final_array[i]
        cur = conn.cursor()
        duration = product[0]
        #Get the id of the station
        if duration:
            query = "SELECT id FROM blog_stations WHERE station_name=%s"
            origin = product[1]
            origin = origin.strip('\n')
            cur.execute(query, [origin])
            origin = cur.fetchone()

            print("Origin", origin)

            query = "SELECT id FROM blog_stations WHERE station_name=%s"
            destination = product[2]
            destination = destination.strip('\n')
            cur.execute(query, [destination])
            destination = cur.fetchone()
            
            print("Destination: ",destination)
            if destination is not None and origin is not None:
                destination= destination[0]
                origin = origin[0]
                cur.execute("SELECT * FROM blog_times WHERE origin=%s AND destination=%s AND duration=%s", [origin, destination, duration])
                val = cur.fetchone()
                if val is None:
                    query = "INSERT INTO blog_times(origin, destination, duration) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING"
                    print("Origin: %s \nDestination: %s \nDuration: %s" %(origin, destination, duration + 1))
                    cur.execute(query, [origin, destination, duration])
            else:
                print(product)
                print("Error occured at %d"%i)
            conn.commit()
    conn.close()

def insert_transfer(station_name):
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query= "SELECT id FROM blog_stations WHERE station_name=%s ;"
    cur.execute(query, [station_name])
    conn.commit()
    val = cur.fetchall()
    
    assert len(val) > 0

    if len(val) > 1:
        #Do an insert 
        value_length = len(val)
        for i in range(value_length):
            destionation_id = val[i][0]
            a = value_length - 1
            while a > i:
                origin_id =  val[a][0]
                cur.execute("SELECT * FROM blog_times WHERE origin=%s AND destination=%s AND duration=5", [origin_id, destionation_id])
                b = cur.fetchone()
                if b is None:
                    query = "INSERT INTO blog_times(origin, destination, duration) VALUES(%s, %s, 5)"
                    cur.execute(query, [origin_id, destionation_id])
                    conn.commit()
                    print('Inserting transfer from ', origin_id, "to ", destionation_id)
                a -= 1 
    conn.close()

def put_to_array(fetch_results):
    results = []

    for result in fetch_results:
        results.append(result[0])

    return results

def insert_in_reverse_order():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query= "SELECT origin, destination, duration FROM blog_times ;"
    cur.execute(query)
    conn.commit()
    val = cur.fetchall()

    for row in val:
        origin = row[0]
        destination = row[1]
        duration = row[2]
        cur.execute("SELECT origin, destination FROM blog_times WHERE origin=%s AND destination=%s;", [destination, origin])
        conn.commit()
        output = cur.fetchall()

        #If there are no inserts
        if not len(output):
            print("Inserting %s, %s, %s "%(origin, destination, duration))
            cur.execute("INSERT INTO blog_times(origin, destination, duration) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING;", [destination,origin , duration])
            conn.commit()
    conn.close()


def get_station_names():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    query= "SELECT station_name FROM blog_stations;"
    cur.execute(query)
    conn.commit()
    val = cur.fetchall()
    return put_to_array(val)

def truncate():
    conn = psycopg2.connect("dbname='memove' user='postgres' host='localhost' password='630991'")
    cur = conn.cursor()
    
    query= "TRUNCATE blog_stations CASCADE;"
    cur.execute(query)
    conn.commit()
    
    query= "TRUNCATE blog_times CASCADE;"
    cur.execute(query)
    conn.commit()

    query= "ALTER SEQUENCE stations_id_seq RESTART WITH 1;"
    cur.execute(query)
    conn.commit()

    query= "ALTER SEQUENCE times_id_seq RESTART WITH 1;"
    cur.execute(query)
    conn.commit()
    
    conn.close()

for i in range(number_of_lines):
    
    #Taking the first_value
    carry_variable = f[i].split(' ')
    first_value = carry_variable[0]
    carry_array = []
    
    #Take the first station name
    if ":" in f[i]:
        for j in range(1, len(carry_variable)):
            carry_array.append(carry_variable[j])
       
    else:
        for j in range(0, len(carry_variable)):
            carry_array.append(carry_variable[j])
    
    first_station_name = ' '.join(carry_array)
    #Delete PM and AM
    first_station_name = first_station_name.replace("PM", "", 1)
    first_station_name = first_station_name.replace("AM", "", 1)
    
    #This is just to block the error that occurs
    index_value = i+2
    if  index_value > number_of_lines:
       break
    
    #Second value
    carry_variable = f[i+1].split(' ')
    second_value = carry_variable[0]
    
    carry_array = []
    
    #Take the second station name
    for j in range(1, len(carry_variable)):
        carry_array.append(carry_variable[j])
    
    second_station_name = ' '.join(carry_array)
    
    #Delete PM and AM
    second_station_name = second_station_name.replace("PM", "", 1)
    second_station_name = second_station_name.replace("AM", "", 1)
    
    #Subtract first_value from the second_value
    first_value = first_value.split(':')
    second_value = second_value.split(':')
    try:
        first_value = int(first_value[0]) * 60 + int(first_value[1])
        second_value = int(second_value[0]) * 60 + int(second_value[1])
    except:
        first_value = 1
        second_value = 1
    
    
    final_value = second_value - first_value 
    
    #Put them together
    product = []
    product.append(final_value)
    
    
    if product[0] > 0:
        product.append(first_station_name)
        product.append(second_station_name)
    else:
        product.append(first_station_name)
        
        if product[0] < 0:
            product.append('This is a transfer')
    
    for element in product:
        if type(element) != type(1):
            element = element.replace('\n', '')
    if '' in product:
        product.remove('')

    #Error detection    
    detect_errors(product, i)

    #Finding the line names and giving them to line_names list
    if not product[0]:
            name = product[1].split(' ')
            if "to" in name:
                if name[0] not in line_names:
                    line_names.append(name[0])

    final_array.append(product)  
file.close()


truncate()
insert_stations()
insert_times()

#To insert Transfers
val = get_station_names()
for name in val:
    insert_transfer(name)
insert_in_reverse_order()

print("Completed!!!")




