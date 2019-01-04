# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading
import requests
import time
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from urlparse import urlparse
from bs4 import BeautifulSoup
from gale_test.settings import NUMBER_OF_THREADS
import Queue
import pyodbc 
import pandas as pd
import math
from copy import deepcopy
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2






def distance(lat1, lon1, lat2, lon2):
    from math import sin, cos, sqrt, atan2, radians
    
    # Manhattan distance
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

# Distance callback

class CreateDistanceCallback(object):
  """Create callback to calculate distances and travel times between points."""

  def __init__(self, locations):
    """Initialize distance array."""
    num_locations = len(locations)
    self.matrix = {}

    for from_node in xrange(num_locations):
      self.matrix[from_node] = {}
      for to_node in xrange(num_locations):
        x1 = locations[from_node][0]
        y1 = locations[from_node][1]
        x2 = locations[to_node][0]
        y2 = locations[to_node][1]
        self.matrix[from_node][to_node] = distance(x1, y1, x2, y2)

  def Distance(self, from_node, to_node):
    return int(self.matrix[from_node][to_node])


# Demand callback
class CreateDemandCallback(object):
  """Create callback to get demands at location node."""

  def __init__(self, demands):
    self.matrix = demands

  def Demand(self, from_node, to_node):
    return self.matrix[from_node]


# Volume callback
class CreateVolumeCallback(object):
  """Create callback to get demands at location node."""

  def __init__(self, volume):
    self.matrix = volume

  def Volume(self, from_node, to_node):
    return self.matrix[from_node]


# Service time (proportional to demand) callback.
class CreateServiceTimeCallback(object):
  """Create callback to get time windows at each location."""

  def __init__(self, demands, time_per_demand_unit):
    self.matrix = demands
    self.time_per_demand_unit = time_per_demand_unit

  def ServiceTime(self, from_node, to_node):
    
    return int(self.time_per_demand_unit)
# Create the travel time callback (equals distance divided by speed).
class CreateTravelTimeCallback(object):
  """Create callback to get travel times between locations."""

  def __init__(self, dist_callback, speed):
    self.dist_callback = dist_callback
    self.speed = speed

  def TravelTime(self, from_node, to_node):
    
    travel_time = self.dist_callback(from_node, to_node) *3600/ self.speed
    
    
    return int(travel_time)
# Create total_time callback (equals service time plus travel time).
class CreateTotalTimeCallback(object):
  """Create callback to get total times between locations."""

  def __init__(self, service_time_callback, travel_time_callback):
    self.service_time_callback = service_time_callback
    self.travel_time_callback = travel_time_callback

  def TotalTime(self, from_node, to_node):
    service_time = self.service_time_callback(from_node, to_node)
    travel_time = self.travel_time_callback(from_node, to_node)
#     print(travel_time,service_time,from_node, to_node)
    
    return service_time + travel_time



def create_data_array():

    import csv
    locations = []
    demands=  []
    locations1 = []
    address = []
    volume = []
    import pdb
    pdb.set_trace()
    with open('/Users/Deepak/git/gale-test/gale_test/gale/test_new.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            import pdb
            pdb.set_trace()
            try:
                volume_ind = float(row['Length'])*float(row['Height'])*float(row['Height'])
                ind = row['location'].index(",")
                check = row['ADDRESS']
                if check in address:
                    ind = address.index(check)
                    
                    demands[ind] = demands[ind] + float(row['Weight'])
                    volume[ind] = volume[ind] + volume_ind
                    
                    
                else:
                    locations.append([float(row['location'][1:ind]),float(row['location'][ind+1:-1])])     
                    demands.append(float(row['Weight']))   
                    address.append(row['ADDRESS'])    
                    volume.append(volume_ind)
            except:
                locations1.append(row)
            
        
       
  


#   locations = [[82, 76], [96, 44], [50, 5], [49, 8], [13, 7], [29, 89], [58, 30], [84, 39],
#                [14, 24], [12, 39], [3, 82], [5, 10], [98, 52], [84, 25], [61, 59], [1, 65],
#                [88, 51], [91, 2], [19, 32], [93, 3], [50, 93], [98, 14], [5, 42], [42, 9],
#                [61, 62], [9, 97], [80, 55], [57, 69], [23, 15], [20, 70], [85, 60], [98, 5]]
# 
#   demands = [0, 19, 21, 6, 19, 7, 12, 16, 6, 16, 8, 14, 21, 16, 3, 22, 18,
#              19, 1, 24, 8, 12, 4, 8, 24, 24, 2, 20, 15, 2, 14, 9]
    
    print(len(locations), sum(demands))
    start_times =  [0] * len(locations)
    
    # tw_duration is the width of the time windows.
    tw_duration = 43200/12*16
    
    # In this example, the width is the same at each location, so we define the end times to be
    # start times + tw_duration. For problems in which the time window widths vary by location,
    # you can explicitly define the list of end_times, as we have done for start_times.
    end_times = [0] * len(start_times)
    
    for i in range(len(start_times)):
      end_times[i] = start_times[i] + tw_duration
    data = [locations, demands, start_times, end_times,volume]
    
    return data









## crawler class to store explored and yet to be explored web pages.
class Crawler:

    

    def __init__(self, link_list = [], images_list=[],explored_list = []):
        Crawler.link_list = link_list
        Crawler.images_list = images_list
        Crawler.explored_list = explored_list

crawler = Crawler() 




# Create your views here.
def home(request):
    template = 'gale/index.html'
    return render(request,template)



## function getting the data from url
def get_data(url,session=None):
    
    
    if session == None:
        session = requests.session()
    try:
        url_data = session.get(url)
        crawler.explored_list.append(url)
    except:
        return None 
    ## using beautiful soup for parsing html##
    soup = BeautifulSoup(url_data.text,"html.parser")
    
    ## getting all the href values
    s1 = soup.find_all('a', href=True)
    links_to_be_shown = []
    for link in s1:
       
        if link['href'] == '' or link['href'][0:2] == '/#' or link['href'][0] == '#' or link['href'][0:2] == '/':
            pass
        else:
            if link['href'][0] == '/':
                final_link = url+link['href']
            else:
                final_link = link['href']
            ## checking if url has http or https
            if urlparse(final_link).scheme in ['http','https'] :
                links_to_be_shown.append(final_link)   
    
    tags_shown = []
    
    ## getting all the image values tags
    tags=soup.findAll('img')
    for tag in tags:
       
        try:
            if tag['data-image'][0:4] == "http":
                tags_shown.append(tag['data-image'])
            else:
                tags_shown.append(url + tag['data-image'])
            

        except:
            pass
        try:
            if tag['src'][0:4] == "http":
                tags_shown.append(tag['src'])
            else:
                tags_shown.append(url + tag['src'])
        except:
            pass
        
    ## storing unique links and images ##
    links_to_be_shown = list(set(links_to_be_shown))
    tags_shown = list(set(tags_shown))
    
    ## returning the data
    data = {}
    data['links'] = links_to_be_shown
    data['images'] = tags_shown
    
    return data
    
    
    
def validate_images(image_list,session):
    
       ## validate the image if its a url
       
       
       ## nit using now as it was affecting the performance of crwaler ###
        valid_images = []
        for images in image_list:
           response = session.get(images)
           if response.status_code == 200:
               valid_images.append(images)
        return valid_images
    
def validate_urls(url_list,session):
    
        ## validate the links if its a proper url
       
       
       ## nit using now as it was affecting the performance of crawler ###
        
        valid_urls = []
        for i in url_list:
            try:
                s = session.get(i)
                valid_urls.append(i)
            except:
                pass
        return valid_urls
    
    
    
    
# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    cd = []
    while True:
        url = queue.get()
        
        data_new = get_data(url)
        if data_newqq!= None:
            crawler.images_list += data_new['images']
            crawler.link_list += data_new['links'] 
        queue.task_done()


# Each queued link is a new job
def create_jobs(seed_urls_to_be_expolred):
    for link in seed_urls_to_be_expolred:
        queue.put(link)
    queue.join()
    


# Check if there are items in the queue, if so crawl them
def crawl(seed_urls_to_be_expolred):
    queued_links = seed_urls_to_be_expolred
    if len(queued_links) > 0:
        
        create_jobs(seed_urls_to_be_expolred)




    
## view for web crawler ##
def substring_indexes(string,substring):
    """ 
    Generate indices of where substring begins in string

    >>> list(find_substring('me', "The cat says meow, meow"))
    [13, 19]
    """
    result = []
    last_found = -1  # Begin at -1 so the next position to search from is 0
    while True:
        # Find next index of substring, by starting after its last known position
        last_found = string.find(substring, last_found + 1)
        if last_found == -1:  
            break  # All occurrences have been found
        else:
            
            result.append(last_found)
    return result
    
def singluar_travel_routes(data):
    
    
    for i in range(len(data)):
        list = []
        seq_drp_list = data[i]['SequencedDropPointsList']
        for j in seq_drp_list:
            try:
                chk_str = j['DropItems']
                result = substring_indexes(chk_str,'<br>')
                for k in range(len(result)):
                    if k == 0:
                        j['DropItems'] = chk_str[:result[k]+len('<br>')]
                    else:
                        j['DropItems'] = chk_str[result[k-1]+len('<br>'):result[k]+len('<br>')]
                        
                    j1 = deepcopy(j)
                    list.append(j1)  
            except:
                list.append(j)
        data[i]['SequencedDropPointsList'] = list
    return data



from django.views.decorators.csrf import csrf_exempt



            

@csrf_exempt
def distance_matrix(request):
    import route_optimizer  
    from multiprocessing.dummy import Pool as ThreadPool 
   
    body = json.loads(request.body)
    
    matrix = body['matrix']
    for i in matrix.keys():
        matrix[int(i)] = matrix.pop(i)
    cd= body['data']
    def matri(cordinates):
        
        try:
            matrix[cordinates[1]][cordinates[2]] = matrix[cordinates[2]][cordinates[1]]  
        
        except:
        ##  if we need to change to osrm point to distance osrm
            matrix[cordinates[1]][cordinates[2]] = route_optimizer.distance_osrm(cordinates[3:])
   
    body = request.body
    
    pool = ThreadPool(16) 
    results = pool.map(matri, cd)
    pool.close() 
    pool.join()#        cd.append(cordinates)
    
    return HttpResponse(json.dumps(matrix) , content_type="application/json")
    #     pool = ThreadPool(16) 
#     results = pool.map(matrix, cd)
#     pool.close() 

@csrf_exempt
def barcode(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.barcode.eanbc import Ean13BarcodeWidget
    from reportlab.graphics import renderPDF
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus.flowables import PageBreak
    from cStringIO import StringIO
    from barcode import label, fill_sheet
    from reportlab.lib.units import inch, mm
    
    barcode_label = request.GET['barcode']
        # Make your response and prep to attach
    filename = 'test'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % (filename)
    tmp = StringIO()

    
    canvas = Canvas(tmp, pagesize= (4*inch, 3*inch))
    for i in range(0,1):
        barcode_label_len= 13-len(barcode_label)
        barcode_label = "0"*barcode_label_len + barcode_label
        sticker = label(barcode_label, 'SHIPPR-PRJ13')
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(10, 65, "Shipment ID")
        canvas.drawString(10, 50, "54320725860")
        canvas.drawString(10, 35, "Delivery on")
        canvas.drawString(10, 20, "18/07/2018")
        canvas.drawString(145, 65, "Ship To:")
        
        address = "House No xyz street 123 Indiranagar Bangalore 560093"
        address = address.split()
        address_str = ""
        address_str_test = ""
        j = 0
        for i in range(len(address)):
            address_str_test += address[i] + str(" ")
            
            if len(address_str_test) > 25:
                address_str_test = address[i] + str(" ")
               
                canvas.drawString(145, 50 - 15*j, address_str)
                j += 1
                address_str = address_str_test
            else:
                address_str = address_str_test
        canvas.drawString(145, 50 - 15*j, address_str)
        
        
        fill_sheet(canvas, sticker)
        canvas.showPage()
    canvas.save()
    
    pdf = tmp.getvalue()
    tmp.close()
    response.write(pdf)
    return response


@csrf_exempt
def noptimize(data,final_data = None, report_id = None,create_new_route = None,report_version = None):
    import route_optimizer
    import datetime
    import time
   
    depot_data  =  data['DepotPoint']
    
    shipments = [0]
    demands=  [0]
    code = [depot_data['Code']]
    data_init = [depot_data]
    address = [depot_data['Address']]
    volume = [0]
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
     
    db = connection.analytics
    collection = db.shipprtech

    locations = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
    if report_id != None:
        new_data = collection.find_one({'_id': report_id })

    
    truck_options= data['UsersRoutePreferences']
    max_weight = 0
    max_vol = 0
    for i in  truck_options['SelectedDeliveryVehicles']:
        if i['Code'] == 'V400':
            VehicleCapacity = int(i['WeightAllowed'])
             
            VolumeCapacity = int(i['VmWtAllowed']) 
            selected_vehicle = i
    if VehicleCapacity == 0:
        for i in  truck_options['SelectedDeliveryVehicles']:
            if i['Code'] == 'V500':
                VehicleCapacity = int(i['WeightAllowed'])
                 
                VolumeCapacity = int(i['VmWtAllowed']) 
                selected_vehicle = i
    if VehicleCapacity == 0:
        for i in  truck_options['SelectedDeliveryVehicles']:
            if i['Code'] == 'V200':
                VehicleCapacity = int(i['WeightAllowed'])
                 
                VolumeCapacity = int(i['VmWtAllowed'])
                selected_vehicle = i 
    VehicleCapacity = 100000
    VolumeCapacity = 100000
    reporting_time =  data['UsersRoutePreferences']['ReportingTimeAtDepotPoint']
    reporting_time =  time.strptime(reporting_time.split(',')[0],'%H:%M')
    
    reporting_time =  int(datetime.timedelta(hours=reporting_time.tm_hour,minutes=reporting_time.tm_min,seconds=reporting_time.tm_sec).total_seconds())
    loading_time = int( data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'])*60
    
    returning_time = data['UsersRoutePreferences']['ReturningTimeAtDepotPoint']
    
    returning_time =  time.strptime(returning_time.split(',')[0],'%H:%M')
    
    returning_time =  int(datetime.timedelta(hours=returning_time.tm_hour,minutes=returning_time.tm_min,seconds=returning_time.tm_sec).total_seconds())
    start_times = [reporting_time + loading_time]
    end_times = [returning_time]
    
    
    
    
    
    data_points = data['SelectedDropointsList']
    cluster_points = data['cluster_info']
    cluster_dict = {}
    cluster_value = {}
    
    for pt in data_points:
        pt['Code'] = pt['Code'] + pt['RouteName']
        cluster_value[pt['Code']] = pt['RouteName']
        try:
            cluster_dict[pt['RouteName']]['code'].append(pt['Code'])
        except:
            cluster_pt = {}
            cluster_pt['code'] = [pt['Code']]
            cluster_pt['cluster_value'] = [0]
            cluster_pt['start_times'] = deepcopy(start_times)
            cluster_pt['end_times'] = deepcopy(end_times)
            cluster_pt['locations'] = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
            cluster_pt['volume'] = [0]
            cluster_pt['address'] = [depot_data['Address']]
            cluster_pt['demands'] = [0]
            cluster_dict[pt['RouteName']] = cluster_pt
     
    
    
    cluster_index = 1
    amount = {}
    for i in data_points:
        
        amount[i['AirwaybillNo']] = {}
        amount[i['AirwaybillNo']]['amount'] = abs(i['NetAmount'])
        amount[i['AirwaybillNo']]['cases'] = abs(i['cases'])
        amount[i['AirwaybillNo']]['desc'] = i['Description']
        if i['PaymentMode'] == '':
            i['PaymentMode'] = 'COD'
        amount[i['AirwaybillNo']]['PaymentMode'] = i['PaymentMode']

       
        
        try:
            cluster_value[i['Code']]
            if i['Wt_kgs'] < 0:
                i['Wt_kgs'] = 0
            if i['DropItemVMwt'] < 0:
                i['DropItemVMwt'] = 0
            
            if i['GoogleMapAddress'] != '':
                
                temp_address =  i['ConsigneeAddress'][:i['ConsigneeAddress'].index(',<br>')]
                temp_address = ''.join(e for e in temp_address if e.isalnum())
                temp_address =  temp_address[:400] + "-" + i['RouteName'] + i['ConsigneeName']               
                check = temp_address
                
                if check in code:
                    indices = [ind_chk for ind_chk, x in enumerate(code) if x == check]
                    
                    ind = indices[len(indices) -1 ]
                    valid_chk = 0
                    if demands[ind] + float( i['Wt_kgs']) > VehicleCapacity:
                        valid_chk = 1
                    if volume[ind] + float(i['DropItemVMwt']) > VolumeCapacity:
                        valid_chk = 1
                    if valid_chk == 0:
                        demands[ind] = demands[ind] + float( i['Wt_kgs'])
                        
                        
                        volume[ind] = volume[ind] + float(i['DropItemVMwt'])
                        
                        ind_cluster = cluster_dict[cluster_value[i['Code']]]['cluster_value'].index(ind)
                        cluster_dict[cluster_value[i['Code']]]['volume'][ind_cluster] +=  float(i['DropItemVMwt'])
                        cluster_dict[cluster_value[i['Code']]]['demands'][ind_cluster] +=  float( i['Wt_kgs'])
                        data_init[ind]['DropItems'] += i['AirwaybillNo']+str("<br>")
                        shipments[ind] = shipments[ind] + 1
                    else:
                        
                        code.append(check)
                        address.append(i['GoogleMapAddress'])
                        
                        try:
    #                         loc = [float(i['lat']), float(i['lng'])]
                            loc = [float(i['lat']), float(i['lng'])]
                            locations.append(loc)
                        except:
                            import pdb
                            pdb.set_trace()
                        
                        try:
                            timeslots = i['TimeSlot']
                            try:
                                start_ind =  timeslots.index('AM')
                                chk_am = 1
                            except:
                                start_ind =  timeslots.index('PM')
                                chk_am = 0
                            try:
                                end_ind = timeslots[start_ind+3:].index('PM')
                                chk_pm = 1
                            except:
                                
                                end_ind = timeslots[start_ind+3:].index('AM')
                                chk_pm = 0
                            
                            start_tm_str = timeslots[:start_ind]
                            end_tm_str =  timeslots[start_ind+3:start_ind+3+end_ind]
                            start_tm_ind = start_tm_str.index(':')
                            end_tm_ind = end_tm_str.index(':')
                            if chk_am == 1:
                                start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                            else:
                                if int(start_tm_str[:start_tm_ind]) == 12:
                                    start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                                else:
                                    start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                            if chk_pm == 1:
                                if int(end_tm_str[:end_tm_ind]) == 12:
                                    end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                                else:
                                    end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 12*3600)
                            else:
                                end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                        except:
                            
                            start_times.append(reporting_time + loading_time)
                            end_times.append(returning_time)
                        
                        i['DropItems'] = i['AirwaybillNo']+str("<br>")
                        data_init.append(i)
                        
                        if i['Wt_kgs'] > VehicleCapacity:
                            return
                       
                        if i['DropItemVMwt'] > VolumeCapacity:
                            return
                        
                        
                        demands.append(i['Wt_kgs'])
                        shipments.append(1)
                        volume.append(i['DropItemVMwt'])
                        
                        
                        cluster_dict[cluster_value[i['Code']]]['cluster_value'].append(cluster_index)
                        cluster_dict[cluster_value[i['Code']]]['start_times'].append(start_times[-1])
                        cluster_dict[cluster_value[i['Code']]]['end_times'].append(end_times[-1]) 
                        cluster_dict[cluster_value[i['Code']]]['locations'].append(loc)
                        cluster_dict[cluster_value[i['Code']]]['volume'].append(i['DropItemVMwt'])
                        cluster_dict[cluster_value[i['Code']]]['address'].append(i['GoogleMapAddress'])
                        
                        cluster_dict[cluster_value[i['Code']]]['demands'].append(i['Wt_kgs'])
                        cluster_index += 1

                        
                        
                    
                else:
                    
                    code.append(check)
                    address.append(i['GoogleMapAddress'])
                    
                    try:
#                         loc = [float(i['lat']), float(i['lng'])]
                        loc = [float(i['lat']), float(i['lng'])]
                        locations.append(loc)
                    except:
                        import pdb
                        pdb.set_trace()
                    
                    try:
                        timeslots = i['TimeSlot']
                        
                        try:
                            start_ind =  timeslots.index('AM')
                            chk_am = 1
                        except:
                            start_ind =  timeslots.index('PM')
                            chk_am = 0
                        try:
                            end_ind = timeslots[start_ind+3:].index('PM')
                            chk_pm = 1
                        except:
                            
                            end_ind = timeslots[start_ind+3:].index('AM')
                            chk_pm = 0
                        
                        start_tm_str = timeslots[:start_ind]
                        end_tm_str =  timeslots[start_ind+3:start_ind+3+end_ind]
                        start_tm_ind = start_tm_str.index(':')
                        end_tm_ind = end_tm_str.index(':')
                        
                        if chk_am == 1:
                            start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                        else:
                            if int(start_tm_str[:start_tm_ind]) == 12:
                                start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                            else:
                                start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                        if chk_pm == 1:
                            
                            if int(end_tm_str[:end_tm_ind]) == 12:
                                end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                            else:
                                end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 12*3600)
                        else:
                            end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                        
                    except:
                        
                        start_times.append(reporting_time + loading_time)
                        end_times.append(returning_time)
                    
                    i['DropItems'] = i['AirwaybillNo']+str("<br>")
                    data_init.append(i)
                    
                    if i['Wt_kgs'] > VehicleCapacity:
                        return
                   
                    if i['DropItemVMwt'] > VolumeCapacity:
                        return
                    
                    
                    demands.append(i['Wt_kgs'])
                    shipments.append(1)
                    volume.append(i['DropItemVMwt'])
                    
                    
                    cluster_dict[cluster_value[i['Code']]]['cluster_value'].append(cluster_index)
                    cluster_dict[cluster_value[i['Code']]]['start_times'].append(start_times[-1])
                    cluster_dict[cluster_value[i['Code']]]['end_times'].append(end_times[-1]) 
                    cluster_dict[cluster_value[i['Code']]]['locations'].append(loc)
                    cluster_dict[cluster_value[i['Code']]]['volume'].append(i['DropItemVMwt'])
                    cluster_dict[cluster_value[i['Code']]]['address'].append(i['GoogleMapAddress'])
                    
                    cluster_dict[cluster_value[i['Code']]]['demands'].append(i['Wt_kgs'])
                    cluster_index += 1
                
        except:
            pass        
    
    for i in  truck_options['SelectedDeliveryVehicles']:
        i['WeightAllowed'] = VehicleCapacity
        i['VmWtAllowed'] = VolumeCapacity
        
    optimized_data = []
    truck_options['number_of_trucks'] = 1    
    for i in cluster_dict.keys():
        
        input_data = [ cluster_dict[i]['locations'], cluster_dict[i]['demands'], cluster_dict[i]['start_times'], cluster_dict[i]['end_times'],cluster_dict[i]['volume'],cluster_dict[i]['address'],cluster_dict[i]['cluster_value']]
        
        
        optimizer_result =  route_optimizer.main(input_data,truck_options)
        
        truck_result = optimizer_result[1]
        if len(optimizer_result[0]) > 0:
            if i == '': 
                optimizer_result[0][0].append("No Route Name")
            else:
                optimizer_result[0][0].append(i)
        optimized_data += optimizer_result[0]
            
    
    
    
    #     cnxn = pyodbc.connect(r'DRIVER={SQL Server};'
    #                       r'Server=MILFOIL.arvixe.com;'
    #                       r'Database=dbShipprTech;'
    #                         r'uid=usrShipprTech;pwd=usr@ShipprTech')
    # 
    #     df = pd.read_sql_query('select * from [dbShipprTech].[dbo].[tDeliveryVehicle]', cnxn)
    #         
    #     final_df = df.loc[df['Code'] == truck_result['Code']]
    #     final_df = final_df.to_dict(orient='records')[0]
    #     final_df['UpdatedAt'] = None
    #     final_df['CreatedAt'] = None
   
    
    total_routes = len(optimized_data)
    
    
    
    
    
    
    result = {}
    result['AllTotalNetAmount'] = "0"
    result['AvgShipmentsCount'] = int(sum(shipments)/total_routes)
    result['DeliveryVehicleModels'] = [{'DeliveryVehicleModel': "Ace", 'DeliveryVehicleCount': total_routes}]
    result['DepotLatitude'] = depot_data['Latitude']
    result['DepotLongitude'] = depot_data['Longitude']
    result['TotalDistanceTravelled'] = 0
    result['TotalHaltTime'] = 0
    result['TotalMassWt'] = sum(demands)
    result['TotalTravelDuration'] = 0
    result['TotalTravelTime'] = 0
    result['DropPointsCount'] = 0
    result['TotalVolumetricWt'] = sum(volume)
    result['TravelRouteCount'] = total_routes
    result['TravelRoutes'] = []
    optimized_data_dict = []
    id = 1
    
    today_date =  datetime.datetime.now().date()
    today_date = datetime.datetime.combine(today_date, datetime.time(00, 00,00))
#     import os
#     os.environ['TZ']='Asia/Kolkata'
#     epoch_format ='%Y-%m-%d %H:%M:%S'
    truck_arrival = (today_date+datetime.timedelta(seconds = reporting_time - 48600)).strftime('%Y-%m-%d  %H:%M:%S')
    truck_departure = (today_date+datetime.timedelta(seconds = reporting_time+loading_time - 48600)).strftime('%Y-%m-%d  %H:%M:%S')
#     truck_arrival = int(time.mktime(time.strptime(truck_arrival,epoch_format)))
#     truck_departure = int(time.mktime(time.strptime(truck_departure,epoch_format)))
    
    for i in optimized_data:
        dict = {}
        
        prev_time = start_times[0]
        last_ind = len(i) - 1
        dict['AllowedVolumetricWeight'] = ''
        dict['DepotName'] = ''
        dict['DropPointsGeoCoordinate'] = []
        #id = i[len(i)-1]
        dict['ID'] = id
        dict['NEWID'] = i[len(i)-1]
        

        
        dict['LimitingParameter'] = "MSWT"
        dict['MajorAreasCovered'] = []
        dict['SequencedDropPointsList'] = []
        
         
        
        
        dict['SuggestedDeliveryVehicle'] = {u'Model': u'Ace', u'DeliveryVehicleTypeCode': u'S', u'Code': u'V400', u'Description': None, u'Brand': u'Tata', u'UpdatedAt': None, u'LockedBy': None, u'IsDropped': False, u'CreatedBy': u'SYS', u'UpdatedBy': u'SYS', u'ShortName': u'Ace', u'StatusCode': u'ACTV', u'FullName': u'Tata Ace', u'CreatedAt': None, u'Dimensions': u'-'}
       
       
        dict['TimeOfArrivalAtDepot'] = truck_arrival
        dict['TimeOfOutForDeliveryFromDepot'] = truck_departure
       
        dict['TimeOfReleasedFromDepot'] = ''
        dict['TimeOfReturnFromForDeliveryAtDepot'] = ''
        dict['TotalDistance'] = 0
        dict['TotalDropItemsCount'] = 0
        dict['TotalDroppointsCount'] = 0
        dict['TotalDuration'] = 0
        dict['TotalHaltTime'] = 0
        dict['TotalMassWeight'] = 0
        dict['TotalNetAmount'] = 0
        dict['TotalQuantity'] = 0
        dict['TotalTravelTime'] = 0
        dict['TotalVolumetricWeight'] = 0
        dict['TravelDate'] = None
        
        result['TotalTravelDuration'] += (int(i[last_ind -1][4]) - prev_time)/60
        
        for j in range(len(i)-1):
            
            node_index = i[j][0]
            try:
                if node_index > 0:
                    
                    data['SelectedDropointsList'][node_index -1 ]['RouteIndex'] = id -1
            except:
                pass

            geo_dict = {}
            geo_dict['DropPointCode'] = code[node_index]
            geo_dict['lat'] = locations[node_index][0]
            geo_dict['lng'] = locations[node_index][1]
            dict['DropPointsGeoCoordinate'].append(geo_dict)
            
            depot_address = address[node_index]
            localities = [x for x, v in enumerate(depot_address) if v == ',']
            try:
                if  depot_address[localities[-1]+2:] != 'India':
                    
                    locality =  depot_address[localities[-3]+2: localities[-2]]
                else:
                    try:
                        locality =  depot_address[localities[-4]+2: localities[-3]]
                    except:
                        pass
                dict['MajorAreasCovered'].append(locality)
            except:
                pass
            
            seq_dp = deepcopy(data_init[node_index])
            
            if node_index > 0:
                if seq_dp['Name'] == None:
                    seq_dp['Name'] = seq_dp['ConsigneeName']
                    
                    
                seconds = reporting_time + loading_time + 3600/int(truck_options['AverageSpeedOfVehicle'])*(i[j][1] + dict['TotalDistance']) + int(truck_options['MHaltTimeAtDropPoint'])*60*(j-1)
                
#                 seconds = int(i[j+1][4])
                seconds = int(seconds)
                    
                
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                if h < 10:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                else:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                if m < 10:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                else:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] += str(m)
                seq_dp['RouteSequentialDrivingDistance'] =  str(i[j][1])
                seq_dp['RouteSequentialPositionIndex'] = j + 1
                seq_dp['Index'] = j+1 
                
            else:
                
                
                
                seq_dp['lat'] = seq_dp['Latitude']
                seq_dp['lng'] = seq_dp['Longitude']
                seq_dp['Name'] = 'Depot_1'
                seq_dp['Index'] = j+1
                if j == 0:
                    
                    seconds = int(reporting_time)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    
                    if h < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                    if m < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str(m)
                    
                    seq_dp['RouteSequentialDrivingDistance'] =  str(0)
                    seq_dp['RouteSequentialPositionIndex'] = j
                else:
                    
                    seconds = reporting_time + loading_time + 3600/int(truck_options['AverageSpeedOfVehicle'])*(i[j][1] + dict['TotalDistance']) + int(truck_options['MHaltTimeAtDropPoint'])*60*(j-1)
                       
#                     seconds = int(i[j][4]) + (3600/int(truck_options['AverageSpeedOfVehicle'])*i[j][1]) + int(truck_options['MHaltTimeAtDropPoint'])*60

                    seconds = int(seconds)

                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    if h < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                    if m < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str(m)
                    
                    seq_dp['RouteSequentialDrivingDistance'] =  str(i[j][1])
                    seq_dp['RouteSequentialPositionIndex'] = j + 1
                    
                    
            try:
                if j > 0:
                    node_index_prev = i[j-1][0]
                    
                    seq_dp['Address'] += "<br>[<a target='_blank' href='https://www.google.com/maps/dir/" + str(locations[node_index_prev][0]) + "," +  str(locations[node_index_prev][1]) + "/" + str(locations[node_index][0]) + "," +  str(locations[node_index][1]) + "'>How To Reach Here</a>]"
            except:
                pass
            seq_dp['RouteIndex'] = id -1
            seq_dp['Route'] = id  - 1
 
            dict['SequencedDropPointsList'].append(seq_dp)
            if j == 0:
                seq = deepcopy(seq_dp)
                seconds_temp = seconds + int(loading_time)
                m, s = divmod(seconds_temp, 60)
                h, m = divmod(m, 60)
                
                if h < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                if m < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str(m)
                seq['RouteSequentialPositionIndex'] += 1
                dict['SequencedDropPointsList'].append(seq)
            if j == len(i) -1 :
                seq = deepcopy(seq_dp)
                seconds_temp = seconds + int(loading_time)
                m, s = divmod(seconds_temp, 60)
                h, m = divmod(m, 60)
                
                if h < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                if m < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str(m)
               
                dict['SequencedDropPointsList'].append(seq)
           
#             seq_dp['Address'] = 
#             seq_dp['Cluster'] =
#             seq_dp['ClusterAngle'] =
#             seq_dp['Code'] =
#             seq_dp['DropItemETA'] =
#             seq_dp['DropItemVMwt'] =
#             seq_dp['DropItems'] =
#             seq_dp['DropItemsCount'] =
#             s
#             seq_dp['GoogleMapAddress'] =
#             seq_dp['HaltTime'] =
#             seq_dp['Index'] =
#             
#             seq_dp['Name'] =
#             seq_dp['RouteSequentialDrivingDistance'] =
#             seq_dp['RouteSequentialPositionIndex'] =
#             seq_dp['lat'] =
#             seq_dp['lng'] =
#             seq_dp['title'] =
#             seq_dp['weight'] =
#             
#             
            
            if j > 0:
                
                dict['TotalDistance']  += i[j][1]
                dict['TotalDropItemsCount'] += shipments[node_index]
            if j > 1:
                
               
                dict['TotalDroppointsCount'] += 1
                dict['TotalDuration'] += (int(i[j][4]) - prev_time)/60
                prev_time = int(i[j][4])
                dict['TotalHaltTime'] += int(truck_options['MHaltTimeAtDropPoint'])
                
                dict['TotalMassWeight'] += demands[i[j-1][0]]
                dict['TotalNetAmount'] = 0
                dict['TotalQuantity'] = 0
                
                   
                dict['TotalVolumetricWeight'] += volume[i[j-1][0]]
        
        
        id += 1 
        dict['TotalTravelTime'] = dict['TotalDuration'] -  dict['TotalHaltTime'] 
        
        sec_time = dict['SequencedDropPointsList'][dict['TotalDroppointsCount'] + 2]['EstimatedTimeOfArrivalForDisplay']
        sec_time = sec_time.split(":")
        ts = int(sec_time[0])*3600 +  int(sec_time[1])*60
        dict['TimeOfReturnFromForDeliveryAtDepot'] = (today_date+datetime.timedelta(seconds = ts - 48600)).strftime('%Y-%m-%d  %H:%M:%S')
        result['TotalHaltTime'] += dict['TotalHaltTime']
        result['TotalDistanceTravelled'] += dict['TotalDistance'] 
        result['DropPointsCount'] += dict['TotalDroppointsCount']
        dict['MajorAreasCovered'] = list(set(dict['MajorAreasCovered']))
        
        result['TravelRoutes'].append(dict)
    
    
    
    result['TotalTravelTime'] = result['TotalTravelDuration'] - result['TotalHaltTime']
            
    
#     result['TravelRoutes'] = singluar_travel_routes(result['TravelRoutes']) 
    
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
    
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
#     cursor.execute('select * from [dbShipprTech].[usrTYP00].[tReport]')
    
    try:
        planning_date = data['Planningdate']
    except:
        planning_date = datetime.datetime.today().strftime('%Y-%m-%d')
    if report_id == None:
        querytreport = "Insert into [dbShipprTech].[usrTYP00].[tReport]([ClientCode],[DepotCode],[ReportDateIST],[Setting_HaltsAtDropPoint],[Setting_HaltsAtDepotPoint],[Setting_TimingsAtDepot],[Setting_AverageSpeedInKMPH],[Setting_MaxAllowedDistanceInKM],[Setting_DV_AllowedVMwt])"
        
        vmwt = ""
        for i in data['UsersRoutePreferences']['SelectedDeliveryVehicles']:
            
                        
            vmwt += i['Code']+":"+str(i['VmWtAllowed']) + "|"
        
        values = str("'") + data['DepotPoint']['ClientCode'] + str("'") +"," + str("'") +data['DepotPoint']['Code'] + str("'") +"," + str("'") +planning_date +  str("'") +"," + str("'") +data['UsersRoutePreferences']['MHaltTimeAtDropPoint'] + str("'") +"," +  str("'") +"Load Time:" + data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'] + "|Release Time:" +  data['UsersRoutePreferences']['ReleasingTimeAtDepotPoint'] + str("'") +"," +  str("'") +"Report Time:" + data['UsersRoutePreferences']['ReportingTimeAtDepotPoint'] + "|Return Time:" +  data['UsersRoutePreferences']['ReturningTimeAtDepotPoint'] + str("'") +"," + str("'") + data['UsersRoutePreferences']['AverageSpeedOfVehicle']  + str("'") +"," + str("'") +data['UsersRoutePreferences']['MaxDistancePerVehicle'] + str("'") +"," +str("'") +vmwt + str("'") 
        
        cursor.execute(querytreport+"Values("+values+")")
        
        conn.commit()
        
        
        trprtid = int(cursor.lastrowid)
        if report_version != None:
            _id = planning_date + str("-") + data['DepotPoint']['Code']
            import pymongo
            from pymongo import MongoClient
            connection = MongoClient('localhost:27017')
    
            db = connection.analytics
            collection = db.shipprtech
            old_data = collection.find_one({'_id': _id })
            
            old_data[report_version]['reports'].append(trprtid)
            
            collection.update({"_id": _id}, old_data)

    else:
        trprtid = report_id
    result['report_id'] = trprtid
    
    ### query for 

    querytreportstr = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteSummary]([ReportID],[RouteCode],[DVCode],[DVInfo],[TravelDistance],[DropPointsCount],[ShipmentsCount],[VolumetricWt],[MassWt],[TravelTimeTotalInMinutes],[TravelTimeHaltInMinutes],[TravelTimeRunningInMinutes],[DepotArrivalTime],[DepotDepartureTime],[DepotReturnTime],[NetAmount],[OnMapRouteColorInHexCode])"
    
    values = ''
    result['summary_id'] = []
    for j in range(len(result['TravelRoutes'])):
        i = result['TravelRoutes'][j]
        values = str("('") + str(trprtid) +  str("'") +"," + str("'") + str(i['NEWID']) + str("'") +"," + str("'") + str(i['SuggestedDeliveryVehicle']['Code']) +  str("'") +"," + str("'")  + str(i['SuggestedDeliveryVehicle']['FullName']) +  str("'") +"," + str("'") + str(i['TotalDistance']) + str("'") +"," + str("'") +str(i['TotalDroppointsCount']) +  str("'") +"," + str("'") + str(i['TotalDropItemsCount']) + str("'") +"," + str("'") +str(i['TotalVolumetricWeight']) + str("'") +"," + str("'") + str(i['TotalMassWeight']) + str("'") +"," + str("'") + str(i['TotalTravelTime']) + str("'") +"," + str("'") +str(i['TotalHaltTime']) + str("'") +"," + str("'") +str(i['TotalDuration']) +  str("'") +"," + str("'") + str(i['TimeOfArrivalAtDepot']) + str("'") +"," + str("'") + str(i['TimeOfOutForDeliveryFromDepot']) + str("'") +"," + str("'") + str(i['TimeOfReturnFromForDeliveryAtDepot']) + str("'") +"," + str("'") + str(i['TotalNetAmount']) + str("'") +"," + str("'") + '#ffffff' + str("')")
        cursor.execute(querytreportstr+"Values"+values)
        
        conn.commit()
        trpsmryid = int(cursor.lastrowid)
        result['summary_id'].append(trpsmryid)
        values_str = ''
        values_box = ''
        treportdetailstr = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteDetail]([DropPointName],[DropPointAddress],[ETA],[Sequence],[ReportID],[ReportRouteSummaryID],[DropPointCode],[DropPointLatitude],[DropPointLongitude],[DropShipmentsUID])"
        routes_len = len(i['SequencedDropPointsList'])
        treportroutebox = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]([ReportID],[ReportRouteSummaryID],[RouteCode],[BoxID],[Sequence], [AmountDue],[Description],[NoOfItems],[PaymentModeCode])"
        for iroute in  range(routes_len): 
            
            routes = i['SequencedDropPointsList'][iroute]
            chk_box = 0
            if iroute == 0:
                routes['DropItems'] = 'Arrival at Depot'
                chk_box = 1
            elif iroute == 1:
                routes['DropItems'] = 'Out For Delivery'
                chk_box = 1
            elif iroute == routes_len -1:
                chk_box = 1
                routes['DropItems'] = 'Return At Depot'
           
            address = routes['Address']    
            
            try:    
            
                add_in = address.index("<br>")
                address = address[:add_in]
            except:
                pass
            address = address.replace("'","")
            try:
                routes['Name'] = routes['Name'].replace("'","")
            except:
                pass
            try:
                routes['DropItems']
            except:
                routes['DropItems'] = 'Return At Depot'
            values_str += str("('") + str(routes['Name']) + str("'") +"," + str("'") +str(address) + str("'") +"," + str("'") +str(routes['EstimatedTimeOfArrivalForDisplay'])+ str("'") +"," + str("'") +str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(routes['Code']) + str("'") +"," + str("'") +str(routes['lat']) + str("'") +"," + str("'") +str(routes['lng'] ) + str("'") +"," + str("'") +str(routes['DropItems']) + str("'),")
            
            if chk_box == 0:
                airway_bill = routes['DropItems'].split("<br>")
                airway_bill = airway_bill[:-1]
                
                for airse in airway_bill:
                    airs1 = airse.split("_")
                    for airs in airs1: 
                        
                        try:            
                            values_box += str("('") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(i['NEWID']) + str("'") +"," + str("'") +str(airs) + str("'") +"," + str("'") + str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") + str(amount[airs]["amount"]) + str("'") +"," + str("'") + str(amount[airs]["desc"]) + str("'") +"," + str("'") + str(amount[airs]["cases"]) +"'," + str("'") + str(amount[airs]["PaymentMode"]) +  str("'),")
                        except:
                            values_box += str("('") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(i['NEWID']) + str("'") +"," + str("'") +str(airs) + str("'") +"," + str("'") + str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") + "0" + str("'") +"," + str("'") + str(amount[airs]["desc"]) + str("'") +"," + str("'") + str(amount[airs]["cases"])+"'," + str("'") + str(amount[airs]["PaymentMode"])+ str("'),")
        values_str = values_str[:len(values_str)-1]
        
        values_box = values_box[:len(values_box)-1]
        
        cursor.execute(treportdetailstr+"Values"+values_str)
        conn.commit()
        
        cursor.execute(treportroutebox+"Values"+values_box)
        
        conn.commit()

        trptcustom = "Insert into [dbShipprTech].[usrTYP00].[tReportCustomized]([ReportID],[ReportRouteSummaryID],[AreaCovered])"
        majorareas = str(i['MajorAreasCovered'])
        majorareas = majorareas.replace("u'","")
        majorareas = majorareas.replace("'","")
        valu_custom = str("('") + str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) +  str("'") +"," + str("'") + majorareas + str("')")
        cursor.execute(trptcustom+"Values"+valu_custom)
        conn.commit()
        
    conn.close()
    #cursor.execute("Values()") ;
    ### report summary######
    
    
    
    
    result['SelectedDropointsList'] = data['SelectedDropointsList']
    
    info = {}
    info['Code'] = 'SUCCESS'
    info['IsPositive'] = 'false'
    info['message'] = ''
    for r in result['TravelRoutes']:
        for k in r['SequencedDropPointsList']:
            try:
                k['Address'] =  k['FullAddress']
            except:
                pass
    
    info['Yield'] = result
    
    
    
    if report_id == None:
        result['_id'] = result['report_id']
         
        result['input_data'] = data
        result['full_data'] = final_data
        result['field_id'] = data['field_id']
        result['first_row'] = data['first_row']
        
         
        collection.insert(result)
         
        result.pop('input_data', None)
    else:
        
        new_data['full_data'] += final_data
        
        
        new_data['TotalMassWt'] += result['TotalMassWt'] 
        new_data['TotalHaltTime'] +=  result['TotalHaltTime']
        new_data['TotalVolumetricWt'] += result['TotalVolumetricWt']
       
        new_data['TotalDistanceTravelled'] +=  result['TotalDistanceTravelled']
        new_data['summary_id'] += result['summary_id']
        new_data['TravelRouteCount'] +=  result['TravelRouteCount']
        new_data['TravelRoutes'] += result['TravelRoutes']
        new_data['TotalTravelDuration'] += result['TotalTravelDuration']
         
        new_data['TotalTravelTime'] += result['TotalTravelTime']
        if create_new_route == None:
            try:
                new_data['reattempt'] += result['TravelRouteCount']
            except:
                new_data['reattempt'] = result['TravelRouteCount']
        else:
            try:
                new_data['add_route'] += result['TravelRouteCount']
            except:
                new_data['add_route'] = result['TravelRouteCount']
        collection.update({"_id": report_id}, new_data)
        
    if report_id == None:
        return HttpResponse(json.dumps(info,) , content_type="application/json")
        
    return_info = info['Yield']
    return_info['input_data'] = data
    if create_new_route != None:
        return_info['report_id'] = report_id
        return_info['Code'] = "NEW ROUTE"
    
    return HttpResponse(json.dumps(return_info,) , content_type="application/json")

@csrf_exempt
def create_excel(request):
    
   
    info = {}
    report_id =  request.GET['report_id']
    query = "SELECT  box.RouteCode as code, box.BoxID as box, box.AmountDue as amountdue,box.AmountPaid as amntpaid,box.DeliveredQuantity as dlvrd_qty,box.DeliveryStateReasonText as dlvd_reason, box.Description as Dsc, box.DeliveryStateReasonText as text,box.FailedQuantity as failedqty,box.FailedReasonText as failedreason,box.NoOfItems as qty,box.RejectedQuantity as rej_qty, box.RejectedReasonText as rej_reason,box.Sequence as seq,route_detail.DropPointCode as DropPointCode,"
    query += " ISNULL(rs.DAName, 'DA NOT ASSIGNED') as da, ISNULL(rs.DriverName, 'Driver NOT ASSIGNED') as drv, rs.DriverContactNumber as drv_number, rs.DAContactNumber as da_number,rs.DVRCNumber as vehicle_number,box.ReportID as rp_Id"
    query +=" FROM[dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]  box "
    query += "join[dbShipprTech].[usrTYP00].[tReportRouteDetail] route_detail"
    query += " on box.ReportRouteSummaryID = route_detail.ReportRouteSummaryID "
    query += "and box.Sequence = route_detail.Sequence "
    query += "left join[dbShipprTech].[usrTYP00].[tReportRouteResource] rs on   box.ReportRouteSummaryID = rs.ReportRouteSummaryID"
    query += " where box.ReportID  =" + report_id
    query += "order by code,seq";
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
    
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
    cursor.execute(query)
    report_id = int(report_id)
    
    
    for row in cursor.fetchall(): 
        info[row['box']] = row
        
    #         row['reportdate'] = dt1
    #         results.append(row) 
    
    
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    data = collection.find_one({'_id': report_id })
    
    full_data =  data['full_data']
    field_id = data['field_id']
    
    for k in full_data:
        key = ''
        
        for k1 in field_id:
            try:
                k[k1] = str(int(float(k[k1])))
            except:
                k[k1] = k[k1]
            key += str(k[k1]) + str("-")
        key = key[:-1]
        
        try:
            k2 = info[key]
            k['Delivered Qty'] = k2['dlvrd_qty']
            k['Rejected Qty'] = k2['rej_qty']
            k['Attempted Qty'] = k2['failedqty']
            if k2['failedqty'] > 0:
                k['Attempted Reason'] = k2['failedreason']
            else:
                k['Attempted Reason'] = ''
            if  k2['rej_qty'] > 0:
                k['Rejected Reason'] = k2['rej_reason']
            else:
                 k['Rejected Reason'] = ''
        except:
            k['Delivered Qty'] = 0
            k['Rejected Qty'] = 0
            k['Attempted Qty'] = 0
            k['Attempted Reason'] = ''
            k['Rejected Reason'] = ''
            
     
    
   
    keys = data['first_row'] + ['Delivered Qty','Rejected Qty','Attempted Qty','Attempted Reason','Rejected Reason']
    import StringIO
    output = StringIO.StringIO()
    from xlsxwriter.workbook import Workbook
    book = Workbook(output, {'in_memory': True})
    bold = book.add_format({'bold': True})

    worksheet = book.add_worksheet('Delivery Detail')       
    
    col = 0
    # Iterate over the data and write it out row by row.
    
    for col in range(len(keys)):
        worksheet.write(0, col, keys[col],bold)
    
    
    row = 1    
    
    for f in full_data:
        for col in range(len(keys)):
            worksheet.write(row, col, f[keys[col]])
        
        row += 1
#
    book.close()
    
    # construct response
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=Delivery.xlsx"
    
    return response
    
    

@csrf_exempt
def inventory_data(request):
    import pymongo
    from pymongo import MongoClient
    import datetime
    today_hour = datetime.datetime.now().hour*60 + datetime.datetime.now().minute
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shippr_inventory
    body = request.body.decode('utf-8')
    body = json.loads(body)
    delievery_date = body['date']
    ProjectCode = body['Projects']
    id =delievery_date + "-" + ProjectCode
    final_data = {}
    total_qty = 0
    starting_inv = 0
    number_sku = 0
    ohd = 0
    info = {}
    
    collectionSum = db.shippr_inventory_summary
    idSum = ProjectCode
    collectionreport = db.report.find_one({'_id': id})
    
    data_sum = collectionSum.find_one({'_id': idSum })
    data_mrp = db.shippr_mrp.find_one({'_id': ProjectCode })
    mrp = {}
    if data_mrp != None:
        mrp = data_mrp['MRPList']
    
    if data_sum != None:
        data_sum = data_sum['inventory_data']
    else:
        data_sum = {}
    
        
    

#         if collectionreport != None:
#             data = data_sum
#         else:


    '''collection reprt already'''
    if collectionreport == None:
        data = collection.find_one({'_id': id })
    else:
        data = None
    if data == None:
        data = {}
        
        if data_sum == {}:
            
            final_data['received_qty'] = total_qty
            final_data['starting_qty'] = starting_inv
            final_data['ohd'] = total_qty + starting_inv
            final_data['number_sku'] = number_sku
            final_data['sku'] = info
            
            return HttpResponse(json.dumps(final_data) , content_type="application/json")
    
    else:
        
        data = data['inventory_data']
        temp = {}
        for i in data:
            try:
                temp[str(int(i['PRODUCT CODE']))] = i
            except:
                temp[str(i['PRODUCT CODE'])] = i
        data = temp
        
    if collectionreport == None:
       
        import pymssql
        server = 'MILFOIL.arvixe.com'
        user = 'usrShipprTech'
        password = 'usr@ShipprTech'
       
        conn = pymssql.connect(server, user, password, "dbShipprTech")
        cursor = conn.cursor(as_dict=True)
        
        cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReport] where ReportDateIST = '" + str(delievery_date) + "' and DepotCode ='" + ProjectCode+ "' order by ID Desc")
        reports = cursor.fetchall()
    
    prev_data = {}
    if len(reports) > 0:
        report_id = reports[0]['ID']
        cursor.execute("SELECT box.RouteCode as code, box.BoxID as box, box.AmountDue as amountdue,box.AmountPaid as amntpaid,ISNULL(box.DeliveredQuantity, 0)  as dlvrd_qty,box.DeliveryStateReasonText as dlvd_reason, box.Description as Dsc, box.DeliveryStateReasonText as text,ISNULL(box.FailedQuantity, 0)  as failedqty,box.FailedReasonText as failedreason,box.NoOfItems as qty,ISNULL(box.RejectedQuantity,0) as rej_qty, box.RejectedReasonText as rej_reason,box.Sequence as seq,route_detail.DropPointCode as DropPointCode, ISNULL(rs.DAName, 'DA NOT ASSIGNED') as da, ISNULL(rs.DriverName, 'Driver NOT ASSIGNED') as drv, rs.DriverContactNumber as drv_number, rs.DAContactNumber as da_number,rs.DVRCNumber as vehicle_number FROM[dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]  box join[dbShipprTech].[usrTYP00].[tReportRouteDetail] route_detail on box.ReportRouteSummaryID = route_detail.ReportRouteSummaryID and box.Sequence = route_detail.Sequence left join[dbShipprTech].[usrTYP00].[tReportRouteResource] rs on   box.ReportRouteSummaryID = rs.ReportRouteSummaryID where box.ReportID  = '" + str(report_id) + "' order by code,seq")
        boxids = cursor.fetchall()
        for box in boxids:
            key =  box['box']
                
            ind = key.index("-")
            if ind != -1:
                key = key[ind+1:]
            if box['drv'] == "Driver NOT ASSIGNED":
                try:
                    prev_data[key]
                    prev_data[key]["left"] += 0
                except:
                    prev_data[key] = {}
                    prev_data[key]["left"] = 0
            else:
                ohd_ret = box['qty']
                if today_hour >= 810:
                   
                    if box['rej_reason'] != 'Damaged Item':
                        
                        ohd_ret = box['dlvrd_qty']
                    else:
                        ohd_ret = box['dlvrd_qty'] + box['rej_qty']
                
                try:
                   
                    prev_data[key]["left"] += ohd_ret
                except:
                    prev_data[key] = {}
                    prev_data[key]["left"] = ohd_ret
                
    ### creating data from present starting = 0
    
    for j in data:
        
        
        key = j
        i = data[j]
        if key != "":
            try:
                qty = float(i['INVOICE QTY'])
            except:
                 qty = 0
            try:
                
                info[key]['rec'] += qty
                info[key]['ohd'] += qty
            except:
                info[key] = {}
                number_sku += 1
                info[key]['desc'] = i['PRODUCT NAME']
                
                if mrp == {}:
                    info[key]['mrp'] = "MRP NOT AVAILABLE"
                else:
                    try:
                        
                        info[key]['mrp'] =  mrp[ str(int(key))]['MRP']
                    except:
                        info[key]['mrp'] = "MRP NOT AVAILABLE"
                info[key]['rec'] = qty
                
                
                info[key]['starting'] = 0
                
                info[key]['ohd'] = qty 
            try:
                info[key]['ohd'] -= prev_data[key]["left"]
                ohd += info[key]['ohd']
                    
            except:
                ohd += qty
                
            total_qty += qty
            
    
    for j in data_sum:
        
        
        key = j
        i = data_sum[j]
        if key != "":
            try:
                qty = float(i['INVOICE QTY'])
            except:
                 qty = 0
            try:
                
                info[key]['starting'] += qty
                info[key]['ohd'] += qty
                ohd += qty
                
            except:
                info[key] = {}
                number_sku += 1
                info[key]['desc'] = i['PRODUCT NAME']
                
                if mrp == {}:
                    info[key]['mrp'] = "MRP NOT AVAILABLE"
                else:
                    try:
                        
                        info[key]['mrp'] =  mrp[ str(int(key))]['MRP']
                    except:
                        info[key]['mrp'] = "MRP NOT AVAILABLE"
                info[key]['rec'] = 0
                try:
                    info[key]['starting'] = qty
                    
                except:
                    info[key]['starting'] = 0
                starting_inv += qty
                info[key]['ohd'] = qty
                if data == {}:
                    try:
                        info[key]['ohd'] -= prev_data[key]["left"]
                        ohd += info[key]['ohd']
                        
                    except:
                        ohd += qty

                else:
                    ohd += qty
            
            
    final_data['received_qty'] = total_qty
    final_data['starting_qty'] = starting_inv
    final_data['ohd'] = ohd
    final_data['number_sku'] = number_sku
    final_data['sku'] = info
    
    return HttpResponse(json.dumps(final_data) , content_type="application/json")
   
@csrf_exempt
def price_mongo(request):
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shippr_mrp
    
    ProjectCode = request.POST['ProjectCode']
    import xlrd
    keys = request.FILES.keys()[0]
    xlsxfile  = request.FILES[keys].read()
    book = xlrd.open_workbook(filename=None, file_contents=xlsxfile)
    worksheet = book.sheet_by_index(0)
    first_row = [] # Header
    for col in range(worksheet.ncols):
        first_row.append( worksheet.cell_value(0,col).replace(".","").upper() )
    
    info = {}
    data = collection.find_one({'_id': ProjectCode })
    if data != None:
        info = data['MRPList']
    for row in range(1, worksheet.nrows):
        
        elm = {}
        for col in range(worksheet.ncols):
            elm[first_row[col]]=worksheet.cell_value(row,col)
        
        info[str(int(elm['MARICO MAT']))]= elm
             
    
        
    
    if data == None:
        result = {}
        result['_id'] =  ProjectCode
        result['MRPList'] = info
        collection.insert(result)
    else:
        collection.update({"_id": ProjectCode},{"MRPList":info})
    
    info['message'] = "Successfully Updated the MRP List"
    return HttpResponse(json.dumps(info) , content_type="application/json")

@csrf_exempt
def redelivery_points(request):
    
    data = request.POST
    
    project_code = data['ProjectCode']
    planning_date = data['Planningdate']
    
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
    
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
    
    query = "SELECT * FROM [dbShipprTech].[usrTYP00].[tRouteBoxRedelivery] redel join [dbShipprTech].[usrTYP00].[tReport] as report on redel.ReportID= report.ID where  redel.RedeliveryDate = '" + planning_date + "'and  redel.StatusCode = 'NEW' and report.DepotCode = '" +project_code  +"'"
    cursor.execute(query)
    full_data = cursor.fetchall()
    conn.close()
    
    redel_data = {}
    for i in full_data:
        try:
            redel_data[i['ReportID']].append(i)
        except:
            redel_data[i['ReportID']] = [i]
    
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
     
    db = connection.analytics
    collection = db.shipprtech
    redelivery = []
    for i in redel_data.keys():
        try:
            redelivery += collection.find_one({'_id': i })['input_data']['SelectedDropointsList']
        except:
            pass
    info = {}
    for i in redelivery:
        info[i['AirwaybillNo']] = i
#          
    datared = []
    for i in full_data:
        try:
            j = info[i['BoxID']]
            j['cases'] = int(i['NoOfItems'])
            j['AirwaybillNo'] = 'REDELIVERY - ' + j['AirwaybillNo']
            
            datared.append(j)
        except:
            pass
    info = {}
    info['Code'] = 'Success'
    info['Yield'] = datared
    if len(datared) > 0:
        info['Message'] = str(len(datared)) +" points are available for redelivery. Continue New Shipment import and the redelivery locations will be appended to the newly imported deliveries."
    else:
        info['Message'] = "No points are available for redelivery."
    
    id = planning_date + str("-") + project_code
    data = collection.find_one({'_id': id })
    if data == None:
        info['external_input'] = False
    else:
        keys = data.keys()
        keys.remove("_id")
        keys = map(int, keys)
        version = max(keys)
        if data[str(version)]["reports"] == []:
            info['external_input'] =True
        else:
            info['external_input'] = False
    
    return HttpResponse(json.dumps(info) , content_type="application/json")
@csrf_exempt
def add_route(request):
    import json
    data = request.POST
    data1 = {}
    data1['DepotPoint'] = json.loads(data['DepotPoint'])
    data1['UsersRoutePreferences'] = json.loads(data['UsersRoutePreferences'])
    data1['Planningdate'] = data['Planningdate']
    data1['SelectedDropointsList'] = json.loads(data['SelectedDropointsList'])
    data1['cluster_info'] =  json.loads(data['cluster_info'])
    data1['IsOCOR'] = data['IsOCOR']
    report_id = int(data['ReportID'])
    
    
    import xlrd
    import datetime
    keys = request.FILES.keys()[0]
    xlsxfile  = request.FILES[keys].read()
    book = xlrd.open_workbook(filename=None, file_contents=xlsxfile)
    worksheet = book.sheet_by_index(0)
    first_row = [] # Header
    for col in range(worksheet.ncols):
        first_row.append( worksheet.cell_value(0,col).replace(".","").upper() )
    # tronsform the workbook to a list of dictionnaries
    final_data =[]
    data = request.POST
    try:
        fields = json.loads(data['Fields'])
    except:
        fields = {'Shipment ID': 0}
    field_final = []
    
    for i in sorted(fields.keys()):
        
        if i.find('Shipment ID') != -1:
            field_final.append(first_row[fields[i]])
    indlist = []
    for kw in field_final:
    
        indlist.append(first_row.index(kw))
   
    for row in range(1, worksheet.nrows):
        
        elm = {}
        for col in range(worksheet.ncols):
            if col in indlist:
                elm[first_row[col]]= str(worksheet.cell_value(row,col))
            else:
                if col == 0:
                    try:
                        elm[first_row[col]]=str(datetime.datetime(*xlrd.xldate_as_tuple(worksheet.cell_value(row,col), book.datemode)))
                    except:
                        elm[first_row[col]]=worksheet.cell_value(row,col)
                else:
                    elm[first_row[col]]=worksheet.cell_value(row,col)
            
        final_data.append(elm)

    if  data['RouteName'] == 'true':
        
        import pymongo
        from pymongo import MongoClient
        connection = MongoClient('localhost:27017')
          
        db = connection.analytics
        collection = db.shipprtech

        new_data = collection.find_one({'_id': report_id })
        allready_routes = []
        for i in  new_data['TravelRoutes']:
            allready_routes.append(i['NEWID'])
        allready_routes = set(allready_routes)
        
        newroutes = []
        for i in data1['SelectedDropointsList']:
           newroutes.append(i['RouteName']) 
        newroutes = set(newroutes)
        commonroutes = list(newroutes.intersection(allready_routes))
        
        if len(commonroutes) > 0:
            info = {}
            info["Code"] = "ALREADY_PRESENT" 
            info["Message"] = "Please remove already present routes " 
            for i in commonroutes:
                info["Message"] += str(i) + " "
            info["Message"] += "From Excel and Upload it again."
            return HttpResponse(json.dumps(info,) , content_type="application/json")
#     

       
        data = noptimize(data1,final_data,report_id,"ADD ROUTE")
        
    else:
        
        data = route(data1,final_data,report_id,"ADD ROUTE")
    
    data['Code'] = "NEW ROUTE"
    data['ReportID'] = report_id
    
    return data
#     import pymongo
#     from pymongo import MongoClient
#     connection = MongoClient('localhost:27017')
#     
#     db = connection.analytics
#     collection = db.shipprtech
#     data = collection.find_one({'_id': report_id })
#     import pymssql
#     server = 'MILFOIL.arvixe.com'
#     user = 'usrShipprTech'
#     password = 'usr@ShipprTech'
#         
#     conn = pymssql.connect(server, user, password, "dbShipprTech")
#     cursor = conn.cursor(as_dict=True)
#     
#     cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReportRouteSummary] where reportID = " + str(report_id) + " order by ID")
#     summary = cursor.fetchall()
#     summary_ind = []
#     for sum in summary:
#         summary_ind.append(sum['ID'])
#         
#     cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReportRouteResource] where reportID = " + str(report_id) + " order by ReportRouteSummaryID")
#     result = cursor.fetchall()
#     conn.close()
#     info = {}
#     for j in range(len(result)):
#         i = result[j]
#         
#         i.pop('CreatedAt', None)
#         i.pop('UpdatedAt', None)
#         i['ReportDateIST'] = str(i['ReportDateIST'])
#         
#         index = summary_ind.index(i['ReportRouteSummaryID'])
#         info[index+1] = i
#     
#     data['DA'] = info
#     data["droplist"] = deepcopy(data["input_data"]["SelectedDropointsList"])




@csrf_exempt
def get_data(request):
    import json
    data = request.POST
    
    _id = data['Planningdate'] + "-" + data['ProjectCode']
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    result = collection.find_one({'_id': _id })
    if result == None:
        result = {}
        result["Code"] = "ALREADY_PRESENT"
        result["Message"] = "No Data found."
        return HttpResponse(json.dumps(result) , content_type="application/json")
    try:
        result = result[data['report_id']]
        result["version"] = data['report_id']
    except:
        keys = result.keys()
        keys.remove("_id")
        keys = map(int, keys)
        version = max(keys)
        result = result[str(version )]
        result["version"] = str(version )
    result["Code"] = "SUCCESS"
    result["Message"] = "Data Retrieval completed successfully."
    return HttpResponse(json.dumps(result) , content_type="application/json")
    
    
 
@csrf_exempt
def searchreport(request):
    data = request.POST
    id =  data['ProjectDate'] + "-" + data['ProjectCode']
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    
    old_data = collection.find_one({'_id': id })
    if old_data != None:
        keys = old_data.keys()
        keys.remove("_id")
        info = {}
        info["Code"] = "RECORD_FOUND"
        cd= []
        for i in keys:
            cd.append(["Version - " + i,old_data[i]["Created"],i])
        info["Yield"] = cd
        return HttpResponse(json.dumps(info) , content_type="application/json")

    else:
        info = {}
        info["Code"] = "RECORD_NOT_FOUND"
        return HttpResponse(json.dumps(info) , content_type="application/json")
@csrf_exempt
def upload_data(request):
    
    import json
    import xlrd
    import datetime
    keys = request.FILES.keys()[0]
    xlsxfile  = request.FILES[keys].read()
    book = xlrd.open_workbook(filename=None, file_contents=xlsxfile)
    worksheet = book.sheet_by_index(0)
    first_row = [] # Header
    for col in range(worksheet.ncols):
        first_row.append( worksheet.cell_value(0,col).replace(".","").upper() )
    # tronsform the workbook to a list of dictionnaries
    final_data =[]
    data = request.POST
    try:
        fields = json.loads(data['Fields'])
    except:
        fields = {'Shipment ID': 0}
    field_final = []
    
    for i in sorted(fields.keys()):
        
        if i.find('Shipment ID') != -1:
            field_final.append(first_row[fields[i]])
    indlist = []
    for kw in field_final:
    
        indlist.append(first_row.index(kw))
   
    for row in range(1, worksheet.nrows):
        
        elm = {}
        for col in range(worksheet.ncols):
            if col in indlist:
                elm[first_row[col]]= str(worksheet.cell_value(row,col))
            else:
                if col == 0:
                    try:
                        elm[first_row[col]]=str(datetime.datetime(*xlrd.xldate_as_tuple(worksheet.cell_value(row,col), book.datemode)))
                    except:
                        elm[first_row[col]]=worksheet.cell_value(row,col)
                else:
                    elm[first_row[col]]=worksheet.cell_value(row,col)
            
        final_data.append(elm)
    

    info = {}
    info['final_data'] = final_data
    
    for keys in data:
        if keys in ['Planningdate','ProjectCode','Created']:
            info[keys] = data[keys]
        else:
            try:
                info[keys] = json.loads(data[keys])
            except:
                info[keys] = data[keys]
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    result = {}
    result['_id'] = info['Planningdate'] + "-" + info['ProjectCode']
    
    old_data = collection.find_one({'_id': result['_id'] })
    info['reports'] = []
    
    if old_data == None:
        
        result["1"] = info 
        
        collection.insert(result)
        info["Message"] = "Uploaded New data. No older version present"
    else:
        
        keys = old_data.keys()
        keys.remove("_id")
        keys = map(int, keys)
        version = max(keys)
        result = old_data
        result[str(version+1)] = info
        
        collection.update({"_id": result["_id"]}, result)
        
        info["Message"] = "Older version present . Created newer version"
    info["Code"] = "SUCCESS"
    
    return HttpResponse(json.dumps(info) , content_type="application/json")
    
@csrf_exempt
def route_mongo(request):

    import json
    import xlrd
    import datetime
    data = request.POST
    field_final = []
    try:
        fields = json.loads(data['Fields'])
    except:
        fields = {'Shipment ID': 0}
    
    first_row = []    
    try:
        
        keys = request.FILES.keys()[0]
        xlsxfile  = request.FILES[keys].read()
        book = xlrd.open_workbook(filename=None, file_contents=xlsxfile)
        worksheet = book.sheet_by_index(0)
    # Header
        for col in range(worksheet.ncols):
            first_row.append( worksheet.cell_value(0,col).replace(".","").upper() )
    # tronsform the workbook to a list of dictionnaries
   
    except:
        data1 = json.loads(data['final_data'])
        first_row =  data1[0].keys()
        
    
    
    
    for i in sorted(fields.keys()):
        
        if i.find('Shipment ID') != -1:
            field_final.append(first_row[fields[i]])
    
    indlist = []
    for kw in field_final:
        
        indlist.append(first_row.index(kw))
    try:
        final_data = []
        for row in range(1, worksheet.nrows):
            
            elm = {}
            for col in range(worksheet.ncols):
                if col in indlist:
                    elm[first_row[col]]= str(worksheet.cell_value(row,col))
                else:
                    if col == 0:
                        try:
                            elm[first_row[col]]=str(datetime.datetime(*xlrd.xldate_as_tuple(worksheet.cell_value(row,col), book.datemode)))
                        except:
                            elm[first_row[col]]=worksheet.cell_value(row,col)
                    else:
                        elm[first_row[col]]=worksheet.cell_value(row,col)
                
            final_data.append(elm)
    except:
        
        final_data = data1
        
        
    
    
    
    data1 = {}
    data1['DepotPoint'] = json.loads(data['DepotPoint'])
    data1['UsersRoutePreferences'] = json.loads(data['UsersRoutePreferences'])
    data1['Planningdate'] = data['Planningdate']
    data1['SelectedDropointsList'] = json.loads(data['SelectedDropointsList'])
    data1['cluster_info'] =  json.loads(data['cluster_info'])
    data1['IsOCOR'] = data['IsOCOR']
    
    
    data1['field_id'] = field_final
    data1['first_row'] = first_row
    
    project_code = data1['DepotPoint']['Code']
    
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
     
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
     
    query = "SELECT * FROM [dbShipprTech].[usrTYP00].[tRouteBoxRedelivery] redel join [dbShipprTech].[usrTYP00].[tReport] as report on redel.ReportID= report.ID where  redel.RedeliveryDate = '" + data1['Planningdate'] + "'and  redel.StatusCode = 'NEW' and report.DepotCode = '" +project_code  +"'"
    cursor.execute(query)
    full_data = cursor.fetchall()
    conn.close()
     
    redel_data = {}
    for i in full_data:
        try:
            redel_data[i['ReportID']].append(i)
        except:
            redel_data[i['ReportID']] = [i]
     
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
      
    db = connection.analytics
    collection = db.shipprtech
    redelivery = []
    cluster_info = []
    for i in redel_data.keys():
        try:
            redelivery += collection.find_one({'_id': i })['input_data']['SelectedDropointsList']
            cluster_info += collection.find_one({'_id': i })['input_data']['cluster_info']
        except:
            pass
    info = {}
    for i in redelivery:
        info[i['AirwaybillNo']] = i
#          
    datared = []
    
    for i in full_data:
        try:
            j = info[i['BoxID']]
            j['cases'] = int(i['NoOfItems'])
            j['AirwaybillNo'] = 'REDELIVERY - ' + j['AirwaybillNo']
            
            datared.append(j)
        except:
            pass
    
    data1['SelectedDropointsList'] += datared
    data1['cluster_info'] += cluster_info
    
    if data["report_version"] == "null":
        report_version = None
    else:
        
        report_version = data["report_version"] 
    if  data['RouteName'] == 'true':
        
        return_data = noptimize(data1,final_data,None,None,report_version)
        
    else:
        
        return_data = route(data1,final_data,None,None,report_version)
     
    
    for report_id in redel_data:
        report_id = int(report_id)
        
        keys = []
        for i in redel_data[report_id]:
            keys.append(i['BoxID'])
        assign_redliver(keys, report_id)

    
    
    
    return(return_data)
@csrf_exempt
def inventory(request):
    delievery_date = request.POST['DeliveryDate']
    ProjectCode = request.POST['ProjectCode']
    import xlrd
    keys = request.FILES.keys()[0]
    xlsxfile  = request.FILES[keys].read()
    book = xlrd.open_workbook(filename=None, file_contents=xlsxfile)
    worksheet = book.sheet_by_index(0)
    first_row = [] # Header
    for col in range(worksheet.ncols):
        first_row.append( worksheet.cell_value(0,col).replace(".","").upper() )
    # tronsform the workbook to a list of dictionnaries
    data =[]
    for row in range(1, worksheet.nrows):
        
        elm = {}
        for col in range(worksheet.ncols):
            elm[first_row[col]]=worksheet.cell_value(row,col)
        
        data.append(elm)
    
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
          
    db = connection.analytics
    collection = db.shippr_inventory
    id = delievery_date + "-" + ProjectCode
    
    
    #data = collection.find_one({'_id': id })
    result = {}
    result['_id'] = id
#     result['allocated'] = Fasle      
    result['inventory_data'] = data
    try:
        collection.insert(result)
    
        data_final = {}
        data_final['Code'] = 'Success'
        data_final['message'] = str(len(data)) + ' rows has been created for above selected Project and Receiving Date' 
    except:
        collection.remove( {"_id":result['_id']});
        collection.insert(result)
    
        data_final = {}
        data_final['Code'] = 'Success'
        data_final['message'] = str(len(data)) + ' rows has been created for above selected Project and Receiving Date. There was already Data Present for selected data and project. New data have overwritten old data' 
    
        
    return HttpResponse(json.dumps(data_final) , content_type="application/json")

def cron_task():
    import datetime
    today_date = str(datetime.datetime.now().date())
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
          
    db = connection.analytics
    collection = db.shippr_inventory
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
   
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
    
    
    info = {}
    info['$regex'] = today_date
    query = {}
    query['_id'] = info
    data = collection.find(query)
   
    for d in data:
        collectionreport = db.report
        try:
            rep  = {}
            rep['_id'] = d['_id']
            collectionreport.insert(rep)
        except:
            pass
        box_dict  = {}
        id =  d['_id'][len(today_date)+1:]
        
        cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReport] where ReportDateIST = '" + str(today_date) + "' and DepotCode ='" + id+ "' order by ID Desc")
        reports = cursor.fetchall()
        if len(reports) > 0:
            report_id = reports[0]['ID']
            
            cursor.execute("SELECT box.RouteCode as code, box.BoxID as box, box.AmountDue as amountdue,box.AmountPaid as amntpaid,ISNULL(box.DeliveredQuantity, 0)  as dlvrd_qty,box.DeliveryStateReasonText as dlvd_reason, box.Description as Dsc, box.DeliveryStateReasonText as text,ISNULL(box.FailedQuantity, 0) as failedqty,box.FailedReasonText as failedreason,box.NoOfItems as qty,ISNULL(box.RejectedQuantity, 0)  as rej_qty, box.RejectedReasonText as rej_reason,box.Sequence as seq,route_detail.DropPointCode as DropPointCode, ISNULL(rs.DAName, 'DA NOT ASSIGNED') as da, ISNULL(rs.DriverName, 'Driver NOT ASSIGNED') as drv, rs.DriverContactNumber as drv_number, rs.DAContactNumber as da_number,rs.DVRCNumber as vehicle_number FROM[dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]  box join[dbShipprTech].[usrTYP00].[tReportRouteDetail] route_detail on box.ReportRouteSummaryID = route_detail.ReportRouteSummaryID and box.Sequence = route_detail.Sequence left join[dbShipprTech].[usrTYP00].[tReportRouteResource] rs on   box.ReportRouteSummaryID = rs.ReportRouteSummaryID where box.ReportID  = '" + str(report_id) + "' order by code,seq")
            boxids = cursor.fetchall()
            for box in boxids:
                key =  box['box']
                ind = key.index("-")
                if ind != -1:
                    key = key[ind+1:]
                
                if box['rej_reason'] != 'Damaged Item':
                   returned_boxes = box['dlvrd_qty']
                else:
                   returned_boxes = box['dlvrd_qty'] + box['rej_qty']
                try:
                    box_dict[key] += returned_boxes
                except:
                    box_dict[key] = returned_boxes
        info = {}   
        for inv in d["inventory_data"]:
            try:
                box_key =  str(int(inv['PRODUCT CODE']))
            except:
                box_key = inv['PRODUCT CODE']
            try:
                
                inv['INVOICE QTY'] -= box_dict[box_key]
                
            except:
                pass
            try:
                info[str(int(inv['PRODUCT CODE']))] = inv 
            except:
                info[str(inv['PRODUCT CODE'])] = inv 
        collection = db.shippr_inventory_summary
        
        data_sum = collection.find_one({'_id': id })
        if data_sum == None:
            result = {}
            result['_id'] = id
            result['inventory_data'] = info
            
            collection.insert(result)
        else:
            data = data_sum["inventory_data"]
            data_keys = set(data.keys())
            info_keys = set(info.keys())
            intersect = info_keys.intersection(data_keys)
            diff = info_keys - data_keys
            
            for i in intersect:
                data[i]['INVOICE QTY'] += info[i]['INVOICE QTY']
            
            for i in diff:
                data[str(i)] = info[i]
            collection.update({"_id": id},{"inventory_data":data})
            
        
    
        
#     info = {}
#     for i in data:
#         info[i['PRODUCT CODE']] = i
#     
#     collection = db.shippr_inventory_summary
#     id = ProjectCode
#     data_sum = collection.find_one({'_id': id })
#     if data_sum == None:
#         result['_id'] = id
#         collection.insert(result)
#     else:
#         keys_already = []
#         for i in data_sum['inventory_data']:
#             try:
#                 i['INVOICE QTY'] += info[i['PRODUCT CODE']]['INVOICE QTY']
#             except:
#                 pass
#             keys_already.append(i['PRODUCT CODE'])
#         keys_already = set(keys_already)
#         
#         info_keys = set(info.keys())
#        
#         diff = info_keys - keys_already
#         
#         for j in diff:
#             data_sum['inventory_data'].append(info[j])
#         
#         collection.update({"_id": id},{"inventory_data":data_sum['inventory_data']})


@csrf_exempt
def redeliver(request):
    
    import json
    
    full_data = json.loads(request.POST['data'])
    report_id = int(request.POST['report_id'])
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    data = collection.find_one({'_id': report_id })['input_data']
    info = {}
    for i in data['SelectedDropointsList']:
        info[i['AirwaybillNo']] = i
        
    data1 = []
    for i in full_data:
        j = info[i[0]]
        j['cases'] = int(i[2])
        data1.append(j)
    
    data['UsersRoutePreferences']['SelectedDeliveryVehicles'] = [json.loads(request.POST['selected_truck'])]
    
    data['SelectedDropointsList'] = deepcopy(data1) 
    
    for i in data['SelectedDropointsList']:
        i['AirwaybillNo'] = "REATTEMPT - " + i['AirwaybillNo'] 
        i['Code'] = i['customercode']
        i['RouteName'] = 1
    data12 = route(data,[],report_id,)
    
    keys = []
    for i in data1:
        keys.append(i['AirwaybillNo'])
    assign_redliver(keys, report_id)
    
    
    return data12


def assign_redliver(keys, reportid):
    
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
        
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
    query = "Update [dbShipprTech].[usrTYP00].[tRouteBoxRedelivery] set StatusCode = 'AssignedtoRoute' where reportID = " + str(reportid) + " and BoxID in ("
    for i in keys:
        query += " '"+ str(i) + "',"
    query = query[:-1] + " )"
    
    cursor.execute(query)
    conn.commit()
    conn.close()
@csrf_exempt
def check_import(request):
    
    data = request.POST
    id = data["ProjectDate"] + str("-") + data["ProjectCode"]
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    try:
        data = collection.find_one({'_id': id })
        keys = data.keys()
        keys.remove("_id")
        keys = map(int, keys)
        version = max(keys)
        info = {}
        if data[str(version)]["reports"] == []:
            info['Code'] = "RECORD_FOUND"
            info["Message"] = "There is an already imported data. Please create route for new version."
        else:
            info['Code'] = "RECORD_NOT_FOUND"
    except:
        info = {}
        info['Code'] = "RECORD_NOT_FOUND"
             
    return HttpResponse(json.dumps(info) , content_type="application/json")

@csrf_exempt
def ReportInfo(request):
    
    report_id = int(request.body.decode('utf-8'))
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
    
    db = connection.analytics
    collection = db.shipprtech
    data = collection.find_one({'_id': report_id })
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
        
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
    
    cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReportRouteSummary] where reportID = " + str(report_id) + " order by ID")
    summary = cursor.fetchall()
    summary_ind = []
    for sum in summary:
        summary_ind.append(sum['ID'])
        
    cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReportRouteResource] where reportID = " + str(report_id) + " order by ReportRouteSummaryID")
    result = cursor.fetchall()
    conn.close()
    info = {}
    for j in range(len(result)):
        i = result[j]
        
        i.pop('CreatedAt', None)
        i.pop('UpdatedAt', None)
        i['ReportDateIST'] = str(i['ReportDateIST'])
        
        index = summary_ind.index(i['ReportRouteSummaryID'])
        info[index+1] = i
    
    data['DA'] = info
    data["droplist"] = deepcopy(data["input_data"]["SelectedDropointsList"])
    return HttpResponse(json.dumps(data) , content_type="application/json")


    


@csrf_exempt
def route(data,final_data = None, report_id = None,create_new_route = None,report_version = None):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    import route_optimizer
    import datetime
    import time
#     body = request.body.decode('utf-8')
#     data = json.loads(body)
    import pymongo
    from pymongo import MongoClient
    connection = MongoClient('localhost:27017')
     
    db = connection.analytics
    collection = db.shipprtech
    
    if report_id != None:
        new_data = collection.find_one({'_id': report_id })
    depot_data  =  data['DepotPoint']
    
    shipments = [0]
    demands=  [0]
    code = [depot_data['Code']]
    data_init = [depot_data]
    address = [depot_data['Address']]
    volume = [0]
    locations = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
                

    truck_options= data['UsersRoutePreferences']
    max_weight = 0
    max_vol = 0
    VehicleCapacity = 0
    for i in  truck_options['SelectedDeliveryVehicles']:
        if i['Code'] == 'V400':
            VehicleCapacity = int(i['WeightAllowed'])
             
            VolumeCapacity = int(i['VmWtAllowed']) 
            selected_vehicle = i
    if VehicleCapacity == 0:
        for i in  truck_options['SelectedDeliveryVehicles']:
            if i['Code'] == 'V500':
                VehicleCapacity = int(i['WeightAllowed'])
                 
                VolumeCapacity = int(i['VmWtAllowed']) 
                selected_vehicle = i
    if VehicleCapacity == 0:
        for i in  truck_options['SelectedDeliveryVehicles']:
            if i['Code'] == 'V200':
                VehicleCapacity = int(i['WeightAllowed'])
                 
                VolumeCapacity = int(i['VmWtAllowed'])
                selected_vehicle = i 
    
    reporting_time =  data['UsersRoutePreferences']['ReportingTimeAtDepotPoint']
    reporting_time =  time.strptime(reporting_time.split(',')[0],'%H:%M')
    
    reporting_time =  int(datetime.timedelta(hours=reporting_time.tm_hour,minutes=reporting_time.tm_min,seconds=reporting_time.tm_sec).total_seconds())
    loading_time = int( data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'])*60
    
    returning_time = data['UsersRoutePreferences']['ReturningTimeAtDepotPoint']
    
    returning_time =  time.strptime(returning_time.split(',')[0],'%H:%M')
    
    returning_time =  int(datetime.timedelta(hours=returning_time.tm_hour,minutes=returning_time.tm_min,seconds=returning_time.tm_sec).total_seconds())
    start_times = [reporting_time + loading_time]
    end_times = [returning_time]
    
    
    
    
    
    data_points = data['SelectedDropointsList']
    cluster_points = data['cluster_info']
    cluster_dict = {}
    cluster_value = {}
    
    for pt in cluster_points:
        
        cluster_value[pt['DropPointCode']] = pt['NewRouteID']
        
        try:
            cluster_dict[pt['NewRouteID']]['code'].append(pt['DropPointCode'])
        except:
            cluster_pt = {}
            
            cluster_pt['code'] = [pt['DropPointCode']]
            cluster_pt['cluster_value'] = [0]
            cluster_pt['start_times'] = deepcopy(start_times)
            cluster_pt['end_times'] = deepcopy(end_times)
            cluster_pt['locations'] = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
            cluster_pt['volume'] = [0]
            cluster_pt['address'] = [depot_data['Address']]
            cluster_pt['demands'] = [0]
            cluster_dict[pt['NewRouteID']] = cluster_pt
           
    
    
    
    cluster_index = 1
    amount = {}
    
    for i in data_points:
        
        amount[i['AirwaybillNo']] = {}
        amount[i['AirwaybillNo']]['amount'] = abs(i['NetAmount'])
        amount[i['AirwaybillNo']]['cases'] = abs(i['cases'])
        amount[i['AirwaybillNo']]['desc'] = i['Description']
        if i['PaymentMode'] == '':
            i['PaymentMode'] = 'COD'
        amount[i['AirwaybillNo']]['PaymentMode'] = i['PaymentMode']
        
        try:
            try:
                cluster_value[i['Code']]
            except:
                cluster_value[i['Code']] = i['Cluster']
            if i['GoogleMapAddress'] != '':
                
                temp_address =  i['ConsigneeAddress'][:i['ConsigneeAddress'].index(',<br>')]
                temp_address = ''.join(e for e in temp_address if e.isalnum())
                temp_address =  temp_address[:400]
                check = i['Code']
                
                if check in code:
                    indices = [ind_chk for ind_chk, x in enumerate(code) if x == check]
                    
                    ind = indices[len(indices) -1 ]
                    valid_chk = 0
                    if demands[ind] + float( i['Wt_kgs']) > VehicleCapacity:
                        valid_chk = 1
                    if volume[ind] + float(i['DropItemVMwt']) > VolumeCapacity:
                        valid_chk = 1
                    if valid_chk == 0:
                        demands[ind] = demands[ind] + float( i['Wt_kgs'])
                        
                        
                        volume[ind] = volume[ind] + float(i['DropItemVMwt'])
                        
                        ind_cluster = cluster_dict[cluster_value[i['Code']]]['cluster_value'].index(ind)
                        cluster_dict[cluster_value[i['Code']]]['volume'][ind_cluster] +=  float(i['DropItemVMwt'])
                        cluster_dict[cluster_value[i['Code']]]['demands'][ind_cluster] +=  float( i['Wt_kgs'])
                        data_init[ind]['DropItems'] += i['AirwaybillNo']+str("<br>")
                        shipments[ind] = shipments[ind] + 1
                    else:
                        
                        code.append(check)
                        address.append(i['GoogleMapAddress'])
                        
                        try:
    #                         loc = [float(i['lat']), float(i['lng'])]
                            loc = [float(i['lat']), float(i['lng'])]
                            locations.append(loc)
                        except:
                            import pdb
                            pdb.set_trace()
                        
                        try:
                            timeslots = i['TimeSlot']
                            try:
                                start_ind =  timeslots.index('AM')
                                chk_am = 1
                            except:
                                start_ind =  timeslots.index('PM')
                                chk_am = 0
                            try:
                                end_ind = timeslots[start_ind+3:].index('PM')
                                chk_pm = 1
                            except:
                                
                                end_ind = timeslots[start_ind+3:].index('AM')
                                chk_pm = 0
                            
                            start_tm_str = timeslots[:start_ind]
                            end_tm_str =  timeslots[start_ind+3:start_ind+3+end_ind]
                            start_tm_ind = start_tm_str.index(':')
                            end_tm_ind = end_tm_str.index(':')
                            if chk_am == 1:
                                start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                            else:
                                if int(start_tm_str[:start_tm_ind]) == 12:
                                    start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                                else:
                                    start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                            if chk_pm == 1:
                                if int(end_tm_str[:end_tm_ind]) == 12:
                                    end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                                else:
                                    end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 12*3600)
                            else:
                                end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                        except:
                            
                            start_times.append(reporting_time + loading_time)
                            end_times.append(returning_time)
                        
                        i['DropItems'] = i['AirwaybillNo']+str("<br>")
                        data_init.append(i)
                        
                        if i['Wt_kgs'] > VehicleCapacity:
                            return
                       
                        if i['DropItemVMwt'] > VolumeCapacity:
                            return
                        
                        
                        demands.append(i['Wt_kgs'])
                        shipments.append(1)
                        volume.append(i['DropItemVMwt'])
                        
                        
                        cluster_dict[cluster_value[i['Code']]]['cluster_value'].append(cluster_index)
                        cluster_dict[cluster_value[i['Code']]]['start_times'].append(start_times[-1])
                        cluster_dict[cluster_value[i['Code']]]['end_times'].append(end_times[-1]) 
                        cluster_dict[cluster_value[i['Code']]]['locations'].append(loc)
                        cluster_dict[cluster_value[i['Code']]]['volume'].append(i['DropItemVMwt'])
                        cluster_dict[cluster_value[i['Code']]]['address'].append(i['GoogleMapAddress'])
                        
                        cluster_dict[cluster_value[i['Code']]]['demands'].append(i['Wt_kgs'])
                        cluster_index += 1

                        
                        
                    
                else:
                    
                    code.append(check)
                    
                    address.append(i['GoogleMapAddress'])
                    
                    try:
#                         loc = [float(i['lat']), float(i['lng'])]
                        loc = [float(i['lat']), float(i['lng'])]
                        locations.append(loc)
                    except:
                        import pdb
                        pdb.set_trace()
                    
                    try:
                        timeslots = i['TimeSlot']
                        try:
                            try:
                                start_ind =  timeslots.index('AM')
                                chk_am = 1
                            except:
                                start_ind =  timeslots.index('PM')
                                chk_am = 0
                            try:
                                end_ind = timeslots[start_ind+3:].index('PM')
                                chk_pm = 1
                            except:
                                
                                end_ind = timeslots[start_ind+3:].index('AM')
                                chk_pm = 0
                            
                            start_tm_str = timeslots[:start_ind]
                            end_tm_str =  timeslots[start_ind+3:start_ind+3+end_ind]
                            start_tm_ind = start_tm_str.index(':')
                            end_tm_ind = end_tm_str.index(':')
                            if chk_am == 1:
                                start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                            else:
                                if int(start_tm_str[:start_tm_ind]) == 12:
                                    start_times.append(3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60 )
                                else:
                                    start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                            if chk_pm == 1:
                                if int(end_tm_str[:end_tm_ind]) == 12:
                                    end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                                else:
                                    end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 12*3600)
                            else:
                                end_times.append((3600*int(end_tm_str[:end_tm_ind]) + int(end_tm_str[end_tm_ind+1:])*60)+ 0)
                        except:
                            try:
                                import re
                                slot_ind = [m.start() for m in re.finditer(':', timeslots)]
                                if len(slot_ind) > 0:
                                    for slt in range(len(slot_ind)):
                                        
                                        hours = timeslots[slot_ind[slt]-2:slot_ind[slt]]
                                        minutes =  timeslots[slot_ind[slt]+1:slot_ind[slt]+3]
                                        if slt == 0:
                                            start_times.append(3600*int(hours) + int(minutes)*60 )
                                        if slt== 1:
                                           end_times.append(3600*int(hours) + int(minutes)*60 )
                                else:
                                    start_times.append(reporting_time + loading_time)
                                    end_times.append(returning_time)
                            except:
                                start_times.append(reporting_time + loading_time)
                                end_times.append(returning_time)
                            
                    except:
                        
                        start_times.append(reporting_time + loading_time)
                        end_times.append(returning_time)
                    
                    i['DropItems'] = i['AirwaybillNo']+str("<br>")
                    data_init.append(i)
                    
                    if i['Wt_kgs'] > VehicleCapacity:
                        return
                   
                    if i['DropItemVMwt'] > VolumeCapacity:
                        return
                    
                    
                    demands.append(i['Wt_kgs'])
                    shipments.append(1)
                    volume.append(i['DropItemVMwt'])
                    
                    cluster_dict[cluster_value[i['Code']]]['cluster_value'].append(cluster_index)
                    cluster_dict[cluster_value[i['Code']]]['start_times'].append(start_times[-1])
                    cluster_dict[cluster_value[i['Code']]]['end_times'].append(end_times[-1]) 
                    cluster_dict[cluster_value[i['Code']]]['locations'].append(loc)
                    cluster_dict[cluster_value[i['Code']]]['volume'].append(i['DropItemVMwt'])
                    cluster_dict[cluster_value[i['Code']]]['address'].append(i['GoogleMapAddress'])
                    
                    cluster_dict[cluster_value[i['Code']]]['demands'].append(i['Wt_kgs'])
                    cluster_index += 1
                
        except:
            pass        
    
    
    optimized_data = []
    truck_options['number_of_trucks'] = 100
    
    for i in cluster_dict.keys():
        
        input_data = [ cluster_dict[i]['locations'], cluster_dict[i]['demands'], cluster_dict[i]['start_times'], cluster_dict[i]['end_times'],cluster_dict[i]['volume'],cluster_dict[i]['address'],cluster_dict[i]['cluster_value']]
        
        optimizer_result =  route_optimizer.main(input_data,truck_options)
        chk = 0
        for results in optimizer_result[0]:
            if (len(results) - 2) == 1:
                if (len(input_data[0]) - 1) > 1:
                    chk = 1
              
        if chk == 1:
            truck_options['number_of_trucks'] = len(optimizer_result[0]) - 1
            try:
                optimizer_result =  route_optimizer.main(input_data,truck_options)
            except:
                pass

        truck_result = optimizer_result[1]
        optimized_data += optimizer_result[0]
        
    
    
    #     cnxn = pyodbc.connect(r'DRIVER={SQL Server};'
    #                       r'Server=MILFOIL.arvixe.com;'
    #                       r'Database=dbShipprTech;'
    #                         r'uid=usrShipprTech;pwd=usr@ShipprTech')
    # 
    #     df = pd.read_sql_query('select * from [dbShipprTech].[dbo].[tDeliveryVehicle]', cnxn)
    #         
    #     final_df = df.loc[df['Code'] == truck_result['Code']]
    #     final_df = final_df.to_dict(orient='records')[0]
    #     final_df['UpdatedAt'] = None
    #     final_df['CreatedAt'] = None
   
    
    total_routes = len(optimized_data)
    
    
    
    try:
        truck_name =  optimizer_result[1]['Name']
        
        if truck_name == 'Piaggio Ape':
            truck_name = 'Ape'
        elif truck_name == 'Tata Ace':
            truck_name = 'Ace'
    except:
        truck_name = 'ACE'
    
    result = {}
    result['AllTotalNetAmount'] = "0"
    result['AvgShipmentsCount'] = int(sum(shipments)/total_routes)
    result['DeliveryVehicleModels'] = [{'DeliveryVehicleModel': truck_name, 'DeliveryVehicleCount': total_routes}]
    result['DepotLatitude'] = depot_data['Latitude']
    result['DepotLongitude'] = depot_data['Longitude']
    result['TotalDistanceTravelled'] = 0
    result['TotalHaltTime'] = 0
    result['TotalMassWt'] = sum(demands)
    result['TotalTravelDuration'] = 0
    result['TotalTravelTime'] = 0
    result['DropPointsCount'] = 0
    result['TotalVolumetricWt'] = sum(volume)
    result['TravelRouteCount'] = total_routes
    result['TravelRoutes'] = []
    optimized_data_dict = []
    id = 1
    
    today_date =  datetime.datetime.now().date()
    today_date = datetime.datetime.combine(today_date, datetime.time(00, 00,00))
#     import os
#     os.environ['TZ']='Asia/Kolkata'
#     epoch_format ='%Y-%m-%d %H:%M:%S'
    truck_arrival = (today_date+datetime.timedelta(seconds = reporting_time - 48600)).strftime('%Y-%m-%d  %H:%M:%S')
    truck_departure = (today_date+datetime.timedelta(seconds = reporting_time+loading_time - 48600)).strftime('%Y-%m-%d  %H:%M:%S')
#     truck_arrival = int(time.mktime(time.strptime(truck_arrival,epoch_format)))
#     truck_departure = int(time.mktime(time.strptime(truck_departure,epoch_format)))
    
    for i in optimized_data:
        
        dict = {}
        
        prev_time = start_times[0]
        last_ind = len(i)
        dict['AllowedVolumetricWeight'] = ''
        dict['DepotName'] = ''
        dict['DropPointsGeoCoordinate'] = []
        dict['ID'] = id
        
        if report_id == None:
            dict['NEWID'] = id
        else:
            if create_new_route != None:
                try:
                    
                    dict['NEWID'] = "ADDED - " + str(id + new_data["add_route"]) 
                except:
                    
                    dict['NEWID'] = "ADDED - " + str(id) 
            else:
                try:
                    
                    dict['NEWID'] = "REATTEMPT - " + str(id + new_data["reattempt"]) 
                except:
                    dict['NEWID'] = "REATTEMPT - " + str(id) 
        
        
        dict['LimitingParameter'] = "MSWT"
        dict['MajorAreasCovered'] = []
        dict['SequencedDropPointsList'] = []
        
         
        
        
        dict['SuggestedDeliveryVehicle'] = {u'Model': truck_name, u'DeliveryVehicleTypeCode': u'S', u'Code': u'V400', u'Description': None, u'Brand': u'Tata', u'UpdatedAt': None, u'LockedBy': None, u'IsDropped': False, u'CreatedBy': u'SYS', u'UpdatedBy': u'SYS', u'ShortName': u'Ace', u'StatusCode': u'ACTV', u'FullName': u'Tata Ace', u'CreatedAt': None, u'Dimensions': u'-'}
       
       
        dict['TimeOfArrivalAtDepot'] = truck_arrival
        dict['TimeOfOutForDeliveryFromDepot'] = truck_departure
       
        dict['TimeOfReleasedFromDepot'] = ''
        dict['TimeOfReturnFromForDeliveryAtDepot'] = ''
        dict['TotalDistance'] = 0
        dict['TotalDropItemsCount'] = 0
        dict['TotalDroppointsCount'] = 0
        dict['TotalDuration'] = 0
        dict['TotalHaltTime'] = 0
        dict['TotalMassWeight'] = 0
        dict['TotalNetAmount'] = 0
        dict['TotalQuantity'] = 0
        dict['TotalTravelTime'] = 0
        dict['TotalVolumetricWeight'] = 0
        dict['TravelDate'] = None
        
        result['TotalTravelDuration'] += (int(i[last_ind -1][4]) - prev_time)/60
        for j in range(len(i)):
            
            node_index = i[j][0]
            try:
                if node_index > 0:
                    
                    data['SelectedDropointsList'][node_index -1 ]['RouteIndex'] = id -1
            except:
                pass
            geo_dict = {}
            geo_dict['DropPointCode'] = code[node_index]
            geo_dict['lat'] = locations[node_index][0]
            geo_dict['lng'] = locations[node_index][1]
            dict['DropPointsGeoCoordinate'].append(geo_dict)
            
            depot_address = address[node_index]
            localities = [x for x, v in enumerate(depot_address) if v == ',']
            try:
                if  depot_address[localities[-1]+2:] != 'India':
                    
                    locality =  depot_address[localities[-3]+2: localities[-2]]
                else:
                    try:
                        locality =  depot_address[localities[-4]+2: localities[-3]]
                    except:
                        pass
                dict['MajorAreasCovered'].append(locality)
            except:
                pass
            
            seq_dp = deepcopy(data_init[node_index])
            
            if node_index > 0:
                if seq_dp['Name'] == None:
                    seq_dp['Name'] = seq_dp['ConsigneeName']
                seconds = reporting_time + loading_time + 3600/int(truck_options['AverageSpeedOfVehicle'])*(i[j][1] + dict['TotalDistance']) + int(truck_options['MHaltTimeAtDropPoint'])*60*(j-1)
                
#                 seconds = int(i[j+1][4])
                seconds = int(seconds)
                    
                
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                if h < 10:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                else:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                if m < 10:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                else:
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] += str(m)
                seq_dp['RouteSequentialDrivingDistance'] =  str(i[j][1])
                seq_dp['RouteSequentialPositionIndex'] = j + 1
                seq_dp['Index'] = j+1 
                
            else:
                
                
                
                seq_dp['lat'] = seq_dp['Latitude']
                seq_dp['lng'] = seq_dp['Longitude']
                seq_dp['Name'] = 'Depot_1'
                seq_dp['Index'] = j+1
                if j == 0:
                    
                    seconds = int(reporting_time)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    
                    if h < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                    if m < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str(m)
                    
                    seq_dp['RouteSequentialDrivingDistance'] =  str(0)
                    seq_dp['RouteSequentialPositionIndex'] = j
                else:
                    
                    seconds = reporting_time + loading_time + 3600/int(truck_options['AverageSpeedOfVehicle'])*(i[j][1] + dict['TotalDistance']) + int(truck_options['MHaltTimeAtDropPoint'])*60*(j-1)
                       
#                     seconds = int(i[j][4]) + (3600/int(truck_options['AverageSpeedOfVehicle'])*i[j][1]) + int(truck_options['MHaltTimeAtDropPoint'])*60

                    seconds = int(seconds)

                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    if h < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                    if m < 10:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                    else:
                        seq_dp['EstimatedTimeOfArrivalForDisplay'] += str(m)
                    
                    seq_dp['RouteSequentialDrivingDistance'] =  str(i[j][1])
                    seq_dp['RouteSequentialPositionIndex'] = j + 1
                    
                    
            try:
                if j > 0:
                    node_index_prev = i[j-1][0]
                    
                    seq_dp['Address'] += "<br>[<a target='_blank' href='https://www.google.com/maps/dir/" + str(locations[node_index_prev][0]) + "," +  str(locations[node_index_prev][1]) + "/" + str(locations[node_index][0]) + "," +  str(locations[node_index][1]) + "'>How To Reach Here</a>]"
            except:
                pass
            seq_dp['RouteIndex'] = id -1
            seq_dp['Route'] = id  - 1
            dict['SequencedDropPointsList'].append(seq_dp)
            if j == 0:
                seq = deepcopy(seq_dp)
                seconds_temp = seconds + int(loading_time)
                m, s = divmod(seconds_temp, 60)
                h, m = divmod(m, 60)
                
                if h < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                if m < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str(m)
                seq['RouteSequentialPositionIndex'] += 1
                dict['SequencedDropPointsList'].append(seq)
            if j == len(i) -1 :
                seq = deepcopy(seq_dp)
                seconds_temp = seconds + int(loading_time)
                m, s = divmod(seconds_temp, 60)
                h, m = divmod(m, 60)
                
                if h < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str("0") + str(h)+str(":")
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":")
                if m < 10:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str("0") + str(m)
                else:
                    seq['EstimatedTimeOfArrivalForDisplay'] += str(m)
               
                dict['SequencedDropPointsList'].append(seq)
           
#             seq_dp['Address'] = 
#             seq_dp['Cluster'] =
#             seq_dp['ClusterAngle'] =
#             seq_dp['Code'] =
#             seq_dp['DropItemETA'] =
#             seq_dp['DropItemVMwt'] =
#             seq_dp['DropItems'] =
#             seq_dp['DropItemsCount'] =
#             s
#             seq_dp['GoogleMapAddress'] =
#             seq_dp['HaltTime'] =
#             seq_dp['Index'] =
#             
#             seq_dp['Name'] =
#             seq_dp['RouteSequentialDrivingDistance'] =
#             seq_dp['RouteSequentialPositionIndex'] =
#             seq_dp['lat'] =
#             seq_dp['lng'] =
#             seq_dp['title'] =
#             seq_dp['weight'] =
#             
#             
            
            if j > 0:
                
                dict['TotalDistance']  += i[j][1]
                dict['TotalDropItemsCount'] += shipments[node_index]
            if j > 1:
                
               
                dict['TotalDroppointsCount'] += 1
                dict['TotalDuration'] += (int(i[j][4]) - prev_time)/60
                prev_time = int(i[j][4])
                dict['TotalHaltTime'] += int(truck_options['MHaltTimeAtDropPoint'])
                
                dict['TotalMassWeight'] += demands[i[j-1][0]]
                dict['TotalNetAmount'] = 0
                dict['TotalQuantity'] = 0
                
                   
                dict['TotalVolumetricWeight'] += volume[i[j-1][0]]
        
        
        id += 1 
        dict['TotalTravelTime'] = dict['TotalDuration'] -  dict['TotalHaltTime'] 
        
        sec_time = dict['SequencedDropPointsList'][dict['TotalDroppointsCount'] + 2]['EstimatedTimeOfArrivalForDisplay']
        sec_time = sec_time.split(":")
        ts = int(sec_time[0])*3600 +  int(sec_time[1])*60
        dict['TimeOfReturnFromForDeliveryAtDepot'] = (today_date+datetime.timedelta(seconds = ts - 48600)).strftime('%Y-%m-%d  %H:%M:%S')
        result['TotalHaltTime'] += dict['TotalHaltTime']
        result['TotalDistanceTravelled'] += dict['TotalDistance'] 
        result['DropPointsCount'] += dict['TotalDroppointsCount']
        dict['MajorAreasCovered'] = list(set(dict['MajorAreasCovered']))
        
        result['TravelRoutes'].append(dict)
    
    
    
    result['TotalTravelTime'] = result['TotalTravelDuration'] - result['TotalHaltTime']
            
   
#     result['TravelRoutes'] = singluar_travel_routes(result['TravelRoutes']) 
  
    import pymssql
    server = 'MILFOIL.arvixe.com'
    user = 'usrShipprTech'
    password = 'usr@ShipprTech'
    
    conn = pymssql.connect(server, user, password, "dbShipprTech")
    cursor = conn.cursor(as_dict=True)
#     cursor.execute('select * from [dbShipprTech].[usrTYP00].[tReport]')
    
    try:
        planning_date = data['Planningdate']
    except:
        planning_date = datetime.datetime.today().strftime('%Y-%m-%d')
   
    if report_id == None:
        querytreport = "Insert into [dbShipprTech].[usrTYP00].[tReport]([ClientCode],[DepotCode],[ReportDateIST],[Setting_HaltsAtDropPoint],[Setting_HaltsAtDepotPoint],[Setting_TimingsAtDepot],[Setting_AverageSpeedInKMPH],[Setting_MaxAllowedDistanceInKM],[Setting_DV_AllowedVMwt])"
        
        vmwt = ""
        for i in data['UsersRoutePreferences']['SelectedDeliveryVehicles']:
            vmwt += i['Code']+":"+i['VmWtAllowed'] + "|"
        
        values = str("'") + data['DepotPoint']['ClientCode'] + str("'") +"," + str("'") +data['DepotPoint']['Code'] + str("'") +"," + str("'") +planning_date +  str("'") +"," + str("'") +data['UsersRoutePreferences']['MHaltTimeAtDropPoint'] + str("'") +"," +  str("'") +"Load Time:" + data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'] + "|Release Time:" +  data['UsersRoutePreferences']['ReleasingTimeAtDepotPoint'] + str("'") +"," +  str("'") +"Report Time:" + data['UsersRoutePreferences']['ReportingTimeAtDepotPoint'] + "|Return Time:" +  data['UsersRoutePreferences']['ReturningTimeAtDepotPoint'] + str("'") +"," + str("'") + data['UsersRoutePreferences']['AverageSpeedOfVehicle']  + str("'") +"," + str("'") +data['UsersRoutePreferences']['MaxDistancePerVehicle'] + str("'") +"," +str("'") +vmwt + str("'") 
        
        cursor.execute(querytreport+"Values("+values+")")
        
        conn.commit()
        
        
        trprtid = int(cursor.lastrowid)
        if report_version != None:
            _id = planning_date + str("-") + data['DepotPoint']['Code']
            import pymongo
            from pymongo import MongoClient
            connection = MongoClient('localhost:27017')
    
            db = connection.analytics
            collection = db.shipprtech
            old_data = collection.find_one({'_id': _id })
            
            old_data[report_version]['reports'].append(trprtid)
            
            collection.update({"_id": _id}, old_data)
            
    else:
        trprtid = report_id
    result['report_id'] = trprtid
    
    ### query for 

    querytreportstr = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteSummary]([ReportID],[RouteCode],[DVCode],[DVInfo],[TravelDistance],[DropPointsCount],[ShipmentsCount],[VolumetricWt],[MassWt],[TravelTimeTotalInMinutes],[TravelTimeHaltInMinutes],[TravelTimeRunningInMinutes],[DepotArrivalTime],[DepotDepartureTime],[DepotReturnTime],[NetAmount],[OnMapRouteColorInHexCode])"
    
    values = ''
    result['summary_id'] = []
    for j in range(len(result['TravelRoutes'])):
        i = result['TravelRoutes'][j]
        values = str("('") + str(trprtid) +  str("'") +"," + str("'") + str(i['ID']) + str("'") +"," + str("'") + str(i['SuggestedDeliveryVehicle']['Code']) +  str("'") +"," + str("'")  + str(i['SuggestedDeliveryVehicle']['FullName']) +  str("'") +"," + str("'") + str(i['TotalDistance']) + str("'") +"," + str("'") +str(i['TotalDroppointsCount']) +  str("'") +"," + str("'") + str(i['TotalDropItemsCount']) + str("'") +"," + str("'") +str(i['TotalVolumetricWeight']) + str("'") +"," + str("'") + str(i['TotalMassWeight']) + str("'") +"," + str("'") + str(i['TotalTravelTime']) + str("'") +"," + str("'") +str(i['TotalHaltTime']) + str("'") +"," + str("'") +str(i['TotalDuration']) +  str("'") +"," + str("'") + str(i['TimeOfArrivalAtDepot']) + str("'") +"," + str("'") + str(i['TimeOfOutForDeliveryFromDepot']) + str("'") +"," + str("'") + str(i['TimeOfReturnFromForDeliveryAtDepot']) + str("'") +"," + str("'") + str(i['TotalNetAmount']) + str("'") +"," + str("'") + '#ffffff' + str("')")
        cursor.execute(querytreportstr+"Values"+values)
        
        conn.commit()
        trpsmryid = int(cursor.lastrowid)
        result['summary_id'].append(trpsmryid)
        values_str = ''
        values_box = ''
        treportdetailstr = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteDetail]([DropPointName],[DropPointAddress],[ETA],[Sequence],[ReportID],[ReportRouteSummaryID],[DropPointCode],[DropPointLatitude],[DropPointLongitude],[DropShipmentsUID])"
        routes_len = len(i['SequencedDropPointsList'])
        treportroutebox = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]([ReportID],[ReportRouteSummaryID],[RouteCode],[BoxID],[Sequence], [AmountDue],[Description],[NoOfItems],[PaymentModeCode])"
        for iroute in  range(routes_len): 
            
            routes = i['SequencedDropPointsList'][iroute]
            chk_box = 0
            if iroute == 0:
                routes['DropItems'] = 'Arrival at Depot'
                chk_box = 1
            elif iroute == 1:
                routes['DropItems'] = 'Out For Delivery'
                chk_box = 1
            elif iroute == routes_len -1:
                chk_box = 1
                routes['DropItems'] = 'Return At Depot'
           
            address = routes['Address']    
            
            try:    
            
                add_in = address.index("<br>")
                address = address[:add_in]
            except:
                pass
            address = address.replace("'","")
            try:
                routes['Name'] = routes['Name'].replace("'","")
            except:
                pass
            try:
                routes['DropItems']
            except:
                routes['DropItems'] = 'Return At Depot'
            values_str += str("('") + str(routes['Name']) + str("'") +"," + str("'") +str(address) + str("'") +"," + str("'") +str(routes['EstimatedTimeOfArrivalForDisplay'])+ str("'") +"," + str("'") +str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(routes['Code']) + str("'") +"," + str("'") +str(routes['lat']) + str("'") +"," + str("'") +str(routes['lng'] ) + str("'") +"," + str("'") +str(routes['DropItems']) + str("'),")
            
            if chk_box == 0:
                airway_bill = routes['DropItems'].split("<br>")
                airway_bill = airway_bill[:-1]
                
                for airse in airway_bill:
                    airs1 = airse.split("_")
                    for airs in airs1: 
                        
                        try:            
                            values_box += str("('") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(i['NEWID']) + str("'") +"," + str("'") +str(airs) + str("'") +"," + str("'") + str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") + str(amount[airs]["amount"]) + str("'") +"," + str("'") + str(amount[airs]["desc"]) + str("'") +"," + str("'") + str(amount[airs]["cases"]) +"'," + str("'") + str(amount[airs]["PaymentMode"]) +  str("'),")
                        except:
                            values_box += str("('") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(i['NEWID']) + str("'") +"," + str("'") +str(airs) + str("'") +"," + str("'") + str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") + "0" + str("'") +"," + str("'") + str(amount[airs]["desc"]) + str("'") +"," + str("'") + str(amount[airs]["cases"])+"'," + str("'") + str(amount[airs]["PaymentMode"])+ str("'),")
        values_str = values_str[:len(values_str)-1]
        
        values_box = values_box[:len(values_box)-1]
        
        cursor.execute(treportdetailstr+"Values"+values_str)
        conn.commit()
        
        cursor.execute(treportroutebox+"Values"+values_box)
        
        conn.commit()

        trptcustom = "Insert into [dbShipprTech].[usrTYP00].[tReportCustomized]([ReportID],[ReportRouteSummaryID],[AreaCovered])"
        majorareas = str(i['MajorAreasCovered'])
        majorareas = majorareas.replace("u'","")
        majorareas = majorareas.replace("'","")
        valu_custom = str("('") + str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) +  str("'") +"," + str("'") + majorareas + str("')")
        cursor.execute(trptcustom+"Values"+valu_custom)
        conn.commit()
        
    conn.close()
    #cursor.execute("Values()") ;
    ### report summary######
    
    
    
    
    
    result['SelectedDropointsList'] = data['SelectedDropointsList']
    
    info = {}
    info['Code'] = 'SUCCESS'
    info['IsPositive'] = 'false'
    info['message'] = ''
    for r in result['TravelRoutes']:
        for k in r['SequencedDropPointsList']:
            try:
                k['Address'] =  k['FullAddress']
            except:
                pass
    
    info['Yield'] = result
    
    
    
    if report_id == None:
        result['_id'] = result['report_id']
         
        result['input_data'] = data
        result['full_data'] = final_data
        result['field_id'] = data['field_id']
        result['first_row'] = data['first_row']
        
         
        collection.insert(result)
         
        result.pop('input_data', None)
    else:
        
        new_data['full_data'] += final_data
        new_data['TotalMassWt'] += result['TotalMassWt'] 
        new_data['TotalHaltTime'] +=  result['TotalHaltTime']
        new_data['TotalVolumetricWt'] += result['TotalVolumetricWt']
       
        new_data['TotalDistanceTravelled'] +=  result['TotalDistanceTravelled']
        new_data['summary_id'] += result['summary_id']
        new_data['TravelRouteCount'] +=  result['TravelRouteCount']
        new_data['TravelRoutes'] += result['TravelRoutes']
        new_data['TotalTravelDuration'] += result['TotalTravelDuration']
         
        new_data['TotalTravelTime'] += result['TotalTravelTime']
        if create_new_route == None:
            try:
                new_data['reattempt'] += result['TravelRouteCount']
            except:
                new_data['reattempt'] = result['TravelRouteCount']
        else:
            try:
                new_data['add_route'] += result['TravelRouteCount']
            except:
                new_data['add_route'] = result['TravelRouteCount']
        collection.update({"_id": report_id}, new_data)
        
    if report_id == None:
        return HttpResponse(json.dumps(info,) , content_type="application/json")
        
    return_info = info['Yield']
    return_info['input_data'] = data
    if create_new_route != None:
        return_info['report_id'] = report_id
        return_info['Code'] = "NEW ROUTE"
    
    return HttpResponse(json.dumps(return_info,) , content_type="application/json")




def web_crawler(request):
    ### get the url ##
    url = request.GET.get('url',None)
    ## get the depth ##
    depth = int(request.GET.get('depth',None))
    
    ## create a session ##
    session = requests.Session()
    ## get the data from the seed url##
    data = get_data(url,session)
    
    ## copying the links from seed web page to be explored ##
    seed_urls_to_be_expolred = data['links']
    
    
    seed_urls_explored = []
    
    ## images explored in the seed page ##
    images_list = data['images']
    if depth == 0:
        ## if depth is 0 then no need to furthur exploration
        seed_urls_explored = seed_urls_to_be_expolred
        
    else:
        
       
        depth_initial = 1
        
         ## if depth is greater than 1 then loop over the number of depth ##
        while depth_initial <= depth:
            ## emptying the temp url
            temp_urls = []
            crawler.images_list = []
            crawler.link_list = []
            ## len of to be explored list is greater than 0
            if len(seed_urls_to_be_expolred) > 0:
                ## multi threading to crawl multi pages ##
                
                ## create worker ##
                create_workers()
                
                ## call the work after creating the workers ##
                crawl(seed_urls_to_be_expolred)
                
                ## temp urls from class of crawler
                temp_urls += crawler.link_list
                images_list +=  crawler.images_list
                
#                 for (i,j) in enumerate(seed_urls_to_be_expolred):
#                     if j not in seed_urls_explored:
#                         try:
#                             new_data = get_data(j,session)
#                             
#                             temp_urls  +=  new_data['links']
#                             images_list +=  new_data['images']
#                             seed_urls_explored.append(j)
#                         except Exception as e:
#                             pass
                    
             
            seed_urls_to_be_expolred = list(set(temp_urls))
            
            
            depth_initial += 1    
        
        if len(seed_urls_to_be_expolred) > 0:
            seed_urls_explored = seed_urls_to_be_expolred + crawler.explored_list   
    final_data = {}
    final_data['links'] = seed_urls_explored
    final_data['images'] = list(set(images_list))
        
    return HttpResponse(json.dumps(final_data) , content_type="application/json")
    
    