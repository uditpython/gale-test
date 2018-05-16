import csv
import pdb



info = {}
out = {}
with open('BLRY/result_19_04.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            info[row['ADDRESS']].append(row['Tracking Id'])
        except:
            info[row['ADDRESS']] = {}
            info[row['ADDRESS']] = []
            info[row['ADDRESS']].append(row['Tracking Id'])
  
def row_count(filename):
    with open(filename) as in_file:
        return sum(1 for _ in in_file)
  
with open('BLRY/result_route_19_04.csv') as csvfile: 
    reader = csv.DictReader(csvfile)
    truckList = []
    trucks = []
    truck_name = []
    initial_truck = ''
    
    last_line_number = row_count('BLRY/result_route_19_04.csv')
    for row in reader:
        
        if row['Address'] in info.keys():
            
            if row['Truck'] != initial_truck:
                
                if trucks != []:
                    truck_name.append(initial_truck)
                    truckList.append(trucks)
                    
                    trucks = info[row['Address']]
                initial_truck =  row['Truck']
            else:
                trucks += info[row['Address']]
                       
        else:
            print row['Address']
            
    
        if reader.line_num == last_line_number:
            truck_name.append(initial_truck)
            truckList.append(trucks)
    max_len = 0
    for i in truckList:
        if len(i) > max_len:
            max_len = len(i)
    trucklist1 = []      
    for i in truckList:
        if len(i) < max_len:
            i = i + ['']*(max_len-len(i))
        trucklist1.append(i)
            
    final_dict = {}
    for i in range(len(truck_name)):
        print len(trucklist1[i])
        final_dict[truck_name[i]] = trucklist1[i]
        
    import pandas
    df = pandas.DataFrame(data= final_dict)
    df.to_csv('shipment_19_04.csv', index=False)
