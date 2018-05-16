filename = raw_input()
output = raw_input()
import math
import csv
import requests
url = 'https://maps.googleapis.com/maps/api/geocode/json'
location = []
new_address = []


def distance(lat1, lon1, lat2, lon2):
    
    from math import sin, cos, sqrt, atan2, radians
    lat11, lon11, lat21, lon21 = lat1, lon1, lat2, lon2

    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = R * c
    
    return dist




with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        
#         address =  row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN']
        
#         address = row['ADDRESS'] + str(" ") +  row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN'] + str(" ,INDIA")
        try:
            address = row['ADDRESS'] + str(" ") +  row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN'] + str(" ,INDIA")
        except:
            address = row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN'] + str(" ,INDIA")
        params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
        results = requests.get(url, params=params).json()['results'] 
        
        while results == []:
            try:
                ind = address.index(", ")
                address = address[ind+2:]
            except:
                try:
                    ind = address.index(" ")
                    address = address[ind+1:]
                except:
                    import pdb
                    pdb.set_trace()
            
            params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
            results = requests.get(url, params=params).json()['results'] 
            
#             address = row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN']
#             params = {'sensor': 'false', 'address': address,'key':'AIzaSyBOtRLrxD2JLwjM5_7Z8iFRCYHbpdQrvjo'}
#             results = requests.get(url, params=params).json()['results']
        if results == []:
            
            location.append([])
        else:
            
            while 'Karnataka' not in results[0]['formatted_address']:
                try:
                    ind = address.index(", ")
                    address = address[ind+2:]
                    params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
                    results = requests.get(url, params=params).json()['results']
                except:
                    try:
                        ind = address.index(" ")
                        address = address[ind+1:]
                        params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
                        results = requests.get(url, params=params).json()['results']
                    except:
                        address = row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN'] + str(" ,INDIA")
                        params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
                        results = requests.get(url, params=params).json()['results']
                        results[0]['formatted_address'] =  'Karnataka ' + results[0]['formatted_address']
                
                
                if len(results) == 0:
                    ind = address.index(" ")
                    address = address[ind+1:]
                    params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
                    results = requests.get(url, params=params).json()['results']
            print results[0]['geometry']['location']['lat'],results[0]['geometry']['location']['lng'] 
            location.append([results[0]['geometry']['location']['lat'],results[0]['geometry']['location']['lng']])
            new_address.append(results[0]['formatted_address'])
            
        

import pandas as pd
csv_input = pd.read_csv(filename)
csv_input['location'] = location  
csv_input['new_address'] = new_address

csv_input.to_csv(output, index=False,encoding='utf-8')