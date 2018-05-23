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
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

queue=Queue.Queue()


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

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def route(request):
    from copy import deepcopy
    import route_optimizer
    import datetime
    import time
    body = request.body.decode('utf-8')
    data = json.loads(body)
    depot_data  =  data['DepotPoint']
    
    shipments = [0]
    demands=  [0]
    code = [depot_data['Code']]
    data_init = [depot_data]
    address = [depot_data['Address']]
    volume = [0]
    locations = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
   
    truck_options= data['UsersRoutePreferences']
    
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
            cluster_pt['locations'] = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
            cluster_pt['volume'] = [0]
            cluster_pt['address'] = [depot_data['Address']]
            cluster_pt['demands'] = [0]
            cluster_dict[pt['NewRouteID']] = cluster_pt
           
    
    
     
    cluster_index = 1
    for i in data_points:
        
        if i['GoogleMapAddress'] != '':
            check = i['Code']
            if check in code:
                
                ind = code.index(check)
                
                demands[ind] = demands[ind] + float( i['weight'])
                volume[ind] = volume[ind] + float( i['DropItemVMwt'])
                
                ind_cluster = cluster_dict[cluster_value[i['Code']]]['cluster_value'].index(ind)
                cluster_dict[cluster_value[i['Code']]]['volume'][ind_cluster] +=  float( i['DropItemVMwt'])
                cluster_dict[cluster_value[i['Code']]]['demands'][ind_cluster] +=  float( i['weight'])
                data_init[ind]['DropItems'] += i['AirwaybillNo']+str("<br>")
                shipments[ind] = shipments[ind] + 1
            else:
                
                code.append(i['Code'])
                address.append(i['GoogleMapAddress'])
                try:
                    loc = [float(i['lat']), float(i['lng'])]
                    locations.append(loc)
                except:
                    import pdb
                    pdb.set_trace()
                
                i['DropItems'] = i['AirwaybillNo']+str("<br>")
                data_init.append(i)
                demands.append( i['weight'])
                shipments.append(1)
                volume.append(i['DropItemVMwt'])
                
                cluster_dict[cluster_value[i['Code']]]['cluster_value'].append(cluster_index)
                cluster_dict[cluster_value[i['Code']]]['locations'].append(loc)
                cluster_dict[cluster_value[i['Code']]]['volume'].append(i['DropItemVMwt'])
                cluster_dict[cluster_value[i['Code']]]['address'].append(i['GoogleMapAddress'])
                cluster_dict[cluster_value[i['Code']]]['demands'].append(i['weight'])
                cluster_index += 1
                
                
    
    start_times =  [0] * len(locations)
    reporting_time =  data['UsersRoutePreferences']['ReportingTimeAtDepotPoint']
    reporting_time =  time.strptime(reporting_time.split(',')[0],'%H:%M')
    
    reporting_time =  int(datetime.timedelta(hours=reporting_time.tm_hour,minutes=reporting_time.tm_min,seconds=reporting_time.tm_sec).total_seconds())
    loading_time = int( data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'])*60
    
    returning_time = data['UsersRoutePreferences']['ReturningTimeAtDepotPoint']
    
    returning_time =  time.strptime(returning_time.split(',')[0],'%H:%M')
    
    returning_time =  int(datetime.timedelta(hours=returning_time.tm_hour,minutes=returning_time.tm_min,seconds=returning_time.tm_sec).total_seconds())
    
    
    start_times =  [reporting_time + loading_time] * len(locations)
    end_times = [returning_time] * len(start_times)
    optimized_data = []
    for i in cluster_dict.keys():
        
        input_data = [ cluster_dict[i]['locations'], cluster_dict[i]['demands'], start_times[0:len(cluster_dict[i]['locations'])], end_times[0:len(cluster_dict[i]['locations'])],cluster_dict[i]['volume'],cluster_dict[i]['address'],cluster_dict[i]['cluster_value']]
    
        optimizer_result =  route_optimizer.main(input_data,truck_options)
        
        truck_result = optimizer_result[1]
        optimized_data += optimizer_result[0]
    
    
    
    cnxn = pyodbc.connect(r'Driver={SQL Server Native Client 11.0};'
                      r'Server=DESKTOP-DFS2OR8;'
                      r'Database=dbShipprTech;'
                      r'Trusted_Connection=yes;'
                      r'uid=DESKTOP-DFS2OR8\\Udit Mital;pwd=Spidy@114')

    df = pd.read_sql_query('select * from [dbShipprTech].[dbo].[tDeliveryVehicle]', cnxn)
        
    final_df = df.loc[df['Code'] == truck_result['Code']]
    final_df = final_df.to_dict(orient='records')[0]
    final_df['UpdatedAt'] = None
    final_df['CreatedAt'] = None
    
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
    truck_arrival = (today_date+datetime.timedelta(seconds = reporting_time)).strftime('%Y-%m-%d  %H:%M:%S')
    truck_departure = (today_date+datetime.timedelta(seconds = reporting_time+loading_time)).strftime('%Y-%m-%d  %H:%M:%S')
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
        
        
        dict['LimitingParameter'] = "MSWT"
        dict['MajorAreasCovered'] = []
        dict['SequencedDropPointsList'] = []
        
         
        
        
        dict['SuggestedDeliveryVehicle'] = final_df
       
        
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
            geo_dict = {}
            geo_dict['DropPointCode'] = code[node_index]
            geo_dict['lat'] = locations[node_index][0]
            geo_dict['lng'] = locations[node_index][1]
            dict['DropPointsGeoCoordinate'].append(geo_dict)
            
            depot_address = address[node_index]
            localities = [x for x, v in enumerate(depot_address) if v == ',']
            if  depot_address[localities[-1]+2:] != 'India':
                locality =  depot_address[localities[-3]+2: localities[-2]]
            else:
                try:
                    locality =  depot_address[localities[-4]+2: localities[-3]]
                except:
                    pass
            dict['MajorAreasCovered'].append(locality)
            seq_dp = deepcopy(data_init[node_index])
            if node_index > 0:
                
                seconds = int(i[j][4])
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":") +str(m)
                seq_dp['RouteSequentialDrivingDistance'] =  str(int(i[j][1]))
                seq_dp['RouteSequentialPositionIndex'] = j+1
            else:
                
                
                
                seq_dp['lat'] = seq_dp['Latitude']
                seq_dp['lng'] = seq_dp['Longitude']
                seq_dp['Name'] = 'Depot_1'
                seq_dp['Index'] = -1
                if j == 0:
                    
                    seconds = int(reporting_time)
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    
                    
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":") +str(m)
                    seq_dp['RouteSequentialDrivingDistance'] =  str(0)
                    seq_dp['RouteSequentialPositionIndex'] = 1
                else:
                    seconds = int(i[j][4])
                    m, s = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    seq_dp['EstimatedTimeOfArrivalForDisplay'] = str(h)+str(":") +str(m)
                    seq_dp['RouteSequentialDrivingDistance'] =  str(int(i[j][1]))
                    seq_dp['RouteSequentialPositionIndex'] = j+1
                    
                    
            try:
                if j > 0:
                    node_index_prev = i[j-1][0]
                    
                    seq_dp['Address'] += "<br>[<a target='_blank' href='https://www.google.com/maps/dir/" + str(locations[node_index_prev][0]) + "," +  str(locations[node_index_prev][1]) + "/" + str(locations[node_index][0]) + "," +  str(locations[node_index][1]) + "'>How To Reach Here</a>]"
            except:
                pass
            seq_dp['RouteIndex'] = id -1
            seq_dp['Route'] = id  - 1
            dict['SequencedDropPointsList'].append(seq_dp)
            
           
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
                
                dict['TotalDistance']  += int(i[j][1])
                dict['TotalDropItemsCount'] += shipments[node_index]
            if j > 1:
                
               
                dict['TotalDroppointsCount'] += 1
                dict['TotalDuration'] += (int(i[j][4]) - prev_time)/60
                prev_time = int(i[j][4])
                dict['TotalHaltTime'] += int(truck_options['MHaltTimeAtDropPoint'])
                dict['TotalMassWeight'] += i[j][2]
                dict['TotalNetAmount'] = 0
                dict['TotalQuantity'] = 0
                
                   
                dict['TotalVolumetricWeight'] = i[j][3]
        
        id += 1 
        dict['TotalTravelTime'] = dict['TotalDuration'] -  dict['TotalHaltTime'] 
        
        dict['TimeOfReturnFromForDeliveryAtDepot'] = (today_date+datetime.timedelta(seconds = reporting_time+loading_time+dict['TotalDuration']*60)).strftime('%Y-%m-%d  %H:%M:%S')
        result['TotalHaltTime'] += dict['TotalHaltTime']
        result['TotalDistanceTravelled'] += dict['TotalDistance'] 
        result['DropPointsCount'] += dict['TotalDroppointsCount']
        dict['MajorAreasCovered'] = list(set(dict['MajorAreasCovered']))
        result['TravelRoutes'].append(dict)
    
    
    
    result['TotalTravelTime'] =     result['TotalTravelDuration'] - result['TotalHaltTime']
            
     
    
    info = {}
    info['Code'] = 'SUCCESS'
    info['IsPositive'] = 'false'
    info['message'] = ''
    info['Yield'] = result
    
    
        
    return HttpResponse(json.dumps(info,) , content_type="application/json")




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
    
    