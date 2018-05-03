filename = '03.05.2018.csv'
import csv
import requests
url = 'https://maps.googleapis.com/maps/api/geocode/json'
location = []
with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        
#         address =  row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN']
        address = row['ADDRESS'] + str(" ") +  row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN'] + str(" ,INDIA")
        params = {'sensor': 'false', 'address': address,'key':'AIzaSyCYM_OqLaSDNkYjeqWsYyregpj9_eI_Tc8'}
        results = requests.get(url, params=params).json()['results'] 
        if results == []:
            import pdb
            pdb.set_trace()
#             address = row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN']
#             params = {'sensor': 'false', 'address': address,'key':'AIzaSyBOtRLrxD2JLwjM5_7Z8iFRCYHbpdQrvjo'}
#             results = requests.get(url, params=params).json()['results']
        if results == []:
            
            location.append([])
        else:
            if int(results[0]['geometry']['location']['lat']) != 12:
                import pdb
                pdb.set_trace()
            print results[0]['geometry']['location']['lat'],results[0]['geometry']['location']['lng'] 
            location.append([results[0]['geometry']['location']['lat'],results[0]['geometry']['location']['lng']])
            
        

import pandas as pd
csv_input = pd.read_csv(filename)
csv_input['location'] = location  
csv_input.to_csv('output_new_18_04_2018.csv', index=False)