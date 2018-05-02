filename = '24.04.2018.csv'
import csv
import requests
url = 'https://maps.googleapis.com/maps/api/geocode/json'
location = []
with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        
        address =  row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN']
        params = {'sensor': 'false', 'address': address,'key':'AIzaSyBOtRLrxD2JLwjM5_7Z8iFRCYHbpdQrvjo'}
        results = requests.get(url, params=params).json()['results'] 
        if results == []:
            address = row['CITY'] + str(" ") + row['STATE'] + str(" ") + row['PIN']
            params = {'sensor': 'false', 'address': address,'key':'AIzaSyBOtRLrxD2JLwjM5_7Z8iFRCYHbpdQrvjo'}
            results = requests.get(url, params=params).json()['results']
        if results == []:
            location.append([])
        else:
            location.append([results[0]['geometry']['location']['lat'],results[0]['geometry']['location']['lng']])
            
        print results  
import pdb
pdb.set_trace()
import pandas as pd
csv_input = pd.read_csv(filename)
csv_input['location'] = location  
csv_input.to_csv('output_new_24_04_2018.csv', index=False)