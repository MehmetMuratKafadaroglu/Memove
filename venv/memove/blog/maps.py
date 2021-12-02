import folium 

def map_maker(pk, latitude, longitude):
    m = folium.Map(location=[latitude,longitude], zoom_start=15)
#    logoIcon = folium.features.CustomIcon('C:/projeler/Mehmet Murat (3)/Mehmet Murat/venv/memove/blog/static/icons/icon.png', icon_size=(27,27))
    folium.Marker([latitude, longitude]).add_to(m)
    x = int(pk)
    return m.save("C:/projeler/Mehmet Murat (3)/Mehmet Murat/venv/memove/blog/static/maps/%d.html"%(x))

def get_cordinates(x, list_number):
    cords = (float(x[list_number].get('latitude')), float(x[list_number].get('longitude')))

    return cords

def get_details(x, list_number):
    cords = (x[list_number].get('slug'), x[list_number].get('id'), x[list_number].get('number_of_beds'), x[list_number].get('price'),x[list_number].get('main_image'))
    # tuple like (slug, 1, 3, 500000)
    return cords

