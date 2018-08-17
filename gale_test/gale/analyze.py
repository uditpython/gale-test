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


def data(drs,comp,date):
    info = {}
    out = {}
    drs_url = 'BLRY/' + drs
    comp_url = 'BLRY/' + comp
   
      
    
    info = {}
    with open(drs_url) as csvfile: 
        reader = csv.DictReader(csvfile)
        
        keys = reader.fieldnames
        
        
        for row in reader:
            for k in keys:
                
                info[row[k]] = k
    import pandas as pd
    csv_input = pd.read_csv(comp_url)    
    route_name = []
    box_id = csv_input['Box ID*'].tolist()
    for i in box_id:
        try:
            route_name.append(info[str(i)])  
        except:
            import pdb
            pdb.set_trace()
    csv_input['Route Name'] =   route_name
    csv_input.to_csv(date+ '.csv', index=False)
    

drs = raw_input()
comp = raw_input()
date = raw_input()
dt = data(drs,comp,date)
