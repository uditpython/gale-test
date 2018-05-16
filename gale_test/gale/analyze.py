import csv
time_speed = 30
halt_time = 20
def distance(input):
    lat1 = input[0]
    lon1 = input[1]
    lat2 = input[2]
    lon2 = input[3]
    import json
    import urllib
    import googlemaps
    gmaps = googlemaps.Client(key='AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8')
    location1 = lat1,lon1
    location2 = lat2,lon2
    result = gmaps.distance_matrix(location1, location2, mode='transit')
    driving_distance = result['rows'][0]['elements'][0]['distance']['value']
    driving_distance = driving_distance/1000
    
    return driving_distance




def data():
    info = {}
    out = {}
    with open('gale/BLRY/output_new.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            info[row['Tracking Id']] = row
      
      
      
    with open('gale/BLRY/op_18.04.12.csv') as csvfile: 
        reader = csv.DictReader(csvfile)
        
        keys = reader.fieldnames
        for i in keys:
            out[i] = []
        for row in reader:
            for k in keys:
                if row[k] != '': 
                    out[k].append([row[k],info[row[k]]['location']])
                    
    return [out,info]

   