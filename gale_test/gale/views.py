# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading
import requests
import time
from django.shortcuts import render
from django.http.response import HttpResponse
import json
import pdb
from pdb import Pdb
try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse
from bs4 import BeautifulSoup
from gale_test.settings import NUMBER_OF_THREADS
try:
    import Queue
except:
    
    import queue as Queue 
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
def noptimize(request):
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
        
        cluster_value[pt['Code']] = pt['RouteName']
        try:
            cluster_dict[pt['RouteName']]['code'].append(pt['Code'])
        except:
            cluster_pt = {}
            cluster_pt['code'] = [pt['Code']]
            cluster_pt['cluster_value'] = [0]
            
            cluster_pt['locations'] = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
            cluster_pt['volume'] = [0]
            cluster_pt['address'] = [depot_data['Address']]
            cluster_pt['demands'] = [0]
            cluster_dict[pt['RouteName']] = cluster_pt
     
    
    
    cluster_index = 1
    amount = {}
    for i in data_points:
        amount[i['AirwaybillNo']] = i['NetAmount']
        try:
            cluster_value[i['Code']]
            
            if i['GoogleMapAddress'] != '':
                
                temp_address =  i['ConsigneeAddress'][:i['ConsigneeAddress'].index(',<br>')]
                temp_address = ''.join(e for e in temp_address if e.isalnum())
                temp_address =  temp_address[:400]
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
                                start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                            if chk_pm == 1:
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
                            start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                        if chk_pm == 1:
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
        
        input_data = [ cluster_dict[i]['locations'], cluster_dict[i]['demands'], start_times[0:len(cluster_dict[i]['locations'])], end_times[0:len(cluster_dict[i]['locations'])],cluster_dict[i]['volume'],cluster_dict[i]['address'],cluster_dict[i]['cluster_value']]
        
        optimizer_result =  route_optimizer.main(input_data,truck_options)
        
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
        last_ind = len(i)
        dict['AllowedVolumetricWeight'] = ''
        dict['DepotName'] = ''
        dict['DropPointsGeoCoordinate'] = []
        dict['ID'] = id
        
        
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
        for j in range(len(i)):
            
            node_index = i[j][0]
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
    try:
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
        querytreport = "Insert into [dbShipprTech].[usrTYP00].[tReport]([ClientCode],[DepotCode],[ReportDateIST],[Setting_HaltsAtDropPoint],[Setting_HaltsAtDepotPoint],[Setting_TimingsAtDepot],[Setting_AverageSpeedInKMPH],[Setting_MaxAllowedDistanceInKM],[Setting_DV_AllowedVMwt])"
        
        vmwt = ""
        for i in data['UsersRoutePreferences']['SelectedDeliveryVehicles']:
            vmwt += i['Code']+":"+str(i['VmWtAllowed']) + "|"
        
        values = str("'") + data['DepotPoint']['ClientCode'] + str("'") +"," + str("'") +data['DepotPoint']['Code'] + str("'") +"," + str("'") +planning_date +  str("'") +"," + str("'") +data['UsersRoutePreferences']['MHaltTimeAtDropPoint'] + str("'") +"," +  str("'") +"Load Time:" + data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'] + "|Release Time:" +  data['UsersRoutePreferences']['ReleasingTimeAtDepotPoint'] + str("'") +"," +  str("'") +"Report Time:" + data['UsersRoutePreferences']['ReportingTimeAtDepotPoint'] + "|Return Time:" +  data['UsersRoutePreferences']['ReturningTimeAtDepotPoint'] + str("'") +"," + str("'") + data['UsersRoutePreferences']['AverageSpeedOfVehicle']  + str("'") +"," + str("'") +data['UsersRoutePreferences']['MaxDistancePerVehicle'] + str("'") +"," +str("'") +vmwt + str("'") 
        
        cursor.execute(querytreport+"Values("+values+")")
        
        conn.commit()
        
        
        trprtid = int(cursor.lastrowid)
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
            treportroutebox = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]([ReportID],[ReportRouteSummaryID],[RouteCode],[BoxID],[Sequence], [AmountDue],[Description],[NoOfItems])"
            for iroute in  range(routes_len): 
                
                routes = i['SequencedDropPointsList'][iroute]
                chk_box = 0
                if iroute == 0:
                    routes['DropItems'] = 'Arrival at Depot'
                    chk_box = 1
                elif iroute == 1:
                    routes['DropItems'] = 'Out For Delivery'
                    chk_box = 1
                elif iroute == routes_len -2:
                    chk_box = 1
                    routes['DropItems'] = 'Return At Depot'
                elif iroute == routes_len -1:
                    chk_box = 1
                    routes['DropItems'] = 'Released from Depot'
                address = routes['Address']    
                
                try:    
                
                    add_in = address.index("<br>")
                    address = address[:add_in]
                except:
                    pass
                address = address.replace("'","")
                values_str += str("('") + str(routes['Name']) + str("'") +"," + str("'") +str(address) + str("'") +"," + str("'") +str(routes['EstimatedTimeOfArrivalForDisplay'])+ str("'") +"," + str("'") +str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(routes['Code']) + str("'") +"," + str("'") +str(routes['lat']) + str("'") +"," + str("'") +str(routes['lng'] ) + str("'") +"," + str("'") +str(routes['DropItems']) + str("'),")
                
                if chk_box == 0:
                    airway_bill = routes['DropItems'].split("<br>")
                    airway_bill = airway_bill[:-1]
                    
                    for airse in airway_bill:
                        airs1 = airse.split("_")
                        for airs in airs1:                            
                            values_box += str("('") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(i['ID']) + str("'") +"," + str("'") +str(airs) + str("'") +"," + str("'") + str(routes['RouteSequentialPositionIndex'] -1 ) + str("'") +"," + str("'") + str(amount[airs]) + str("'") +"," + str("'") + str(routes['Description']) + str("'") +"," + str("'") + str(routes['cases']) + str("'),")
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
    
    except:
        pass
    
    
    
   
    
    info = {}
    info['Code'] = 'SUCCESS'
    info['IsPositive'] = 'false'
    info['message'] = ''
    info['Yield'] = result
    try:
        
        import pymongo
        from pymongo import MongoClient
        connection = MongoClient('localhost:27017')
         
        db = connection.analytics
        collection = db.shipprtech
        result['_id'] = result['report_id']
         
        result['input_data'] = data
         
        collection.insert(result)
         
        result.pop('input_data', None)
    except:
        pass    
    
    
    return HttpResponse(json.dumps(info,) , content_type="application/json")


@csrf_exempt
def ReportInfo(request):
    import pdb
    pdb.set_trace()
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
    
    cursor.execute("SELECT * from  [dbShipprTech].[usrTYP00].[tReportRouteResource] where reportID = " + str(report_id) + " order by ")
    result = cursor.fetchall()
    conn.close()
    info = {}
    for i in result:
        i.pop('CreatedAt', None)
        i.pop('UpdatedAt', None)
        i['ReportDateIST'] = str(i['ReportDateIST'])
        info[i['RouteCode']] = i
    
    data['DA'] = info
    
    return HttpResponse(json.dumps(data) , content_type="application/json")


    


@csrf_exempt
def route(request):
    
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
            
            cluster_pt['locations'] = [[float(depot_data['Latitude']), float(depot_data['Longitude'])]]
            cluster_pt['volume'] = [0]
            cluster_pt['address'] = [depot_data['Address']]
            cluster_pt['demands'] = [0]
            cluster_dict[pt['NewRouteID']] = cluster_pt
           
    
    
    
    cluster_index = 1
    amount = {}
    for i in data_points:
        amount[i['AirwaybillNo']] = i['NetAmount']
        try:
            cluster_value[i['Code']]
            
            if i['GoogleMapAddress'] != '':
                
                temp_address =  i['ConsigneeAddress'][:i['ConsigneeAddress'].index(',<br>')]
                temp_address = ''.join(e for e in temp_address if e.isalnum())
                temp_address =  temp_address[:400]
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
                                start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                            if chk_pm == 1:
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
                            start_times.append((3600*int(start_tm_str[:start_tm_ind]) + int(start_tm_str[start_tm_ind+1:])*60) + 12*3600)
                        if chk_pm == 1:
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
        
        input_data = [ cluster_dict[i]['locations'], cluster_dict[i]['demands'], start_times[0:len(cluster_dict[i]['locations'])], end_times[0:len(cluster_dict[i]['locations'])],cluster_dict[i]['volume'],cluster_dict[i]['address'],cluster_dict[i]['cluster_value']]
        
        optimizer_result =  route_optimizer.main(input_data,truck_options)
        
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
        last_ind = len(i)
        dict['AllowedVolumetricWeight'] = ''
        dict['DepotName'] = ''
        dict['DropPointsGeoCoordinate'] = []
        dict['ID'] = id
        
        
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
        for j in range(len(i)):
            
            node_index = i[j][0]
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
    try:
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
        querytreport = "Insert into [dbShipprTech].[usrTYP00].[tReport]([ClientCode],[DepotCode],[ReportDateIST],[Setting_HaltsAtDropPoint],[Setting_HaltsAtDepotPoint],[Setting_TimingsAtDepot],[Setting_AverageSpeedInKMPH],[Setting_MaxAllowedDistanceInKM],[Setting_DV_AllowedVMwt])"
        
        vmwt = ""
        for i in data['UsersRoutePreferences']['SelectedDeliveryVehicles']:
            vmwt += i['Code']+":"+i['VmWtAllowed'] + "|"
        
        values = str("'") + data['DepotPoint']['ClientCode'] + str("'") +"," + str("'") +data['DepotPoint']['Code'] + str("'") +"," + str("'") +planning_date +  str("'") +"," + str("'") +data['UsersRoutePreferences']['MHaltTimeAtDropPoint'] + str("'") +"," +  str("'") +"Load Time:" + data['UsersRoutePreferences']['LoadingTimeAtDepotPoint'] + "|Release Time:" +  data['UsersRoutePreferences']['ReleasingTimeAtDepotPoint'] + str("'") +"," +  str("'") +"Report Time:" + data['UsersRoutePreferences']['ReportingTimeAtDepotPoint'] + "|Return Time:" +  data['UsersRoutePreferences']['ReturningTimeAtDepotPoint'] + str("'") +"," + str("'") + data['UsersRoutePreferences']['AverageSpeedOfVehicle']  + str("'") +"," + str("'") +data['UsersRoutePreferences']['MaxDistancePerVehicle'] + str("'") +"," +str("'") +vmwt + str("'") 
        
        cursor.execute(querytreport+"Values("+values+")")
        
        conn.commit()
        
        
        trprtid = int(cursor.lastrowid)
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
            treportroutebox = "Insert into [dbShipprTech].[usrTYP00].[tReportRouteBoxDelivery]([ReportID],[ReportRouteSummaryID],[RouteCode],[BoxID],[Sequence], [AmountDue])"
            for iroute in  range(routes_len): 
                
                routes = i['SequencedDropPointsList'][iroute]
                chk_box = 0
                if iroute == 0:
                    routes['DropItems'] = 'Arrival at Depot'
                    chk_box = 1
                elif iroute == 1:
                    routes['DropItems'] = 'Out For Delivery'
                    chk_box = 1
                elif iroute == routes_len -2:
                    chk_box = 1
                    routes['DropItems'] = 'Return At Depot'
                elif iroute == routes_len -1:
                    chk_box = 1
                    routes['DropItems'] = 'Released from Depot'
                address = routes['Address']    
                
                try:    
                
                    add_in = address.index("<br>")
                    address = address[:add_in]
                except:
                    pass
                address = address.replace("'","")
                routes['Name'] = routes['Name'].replace("'","")
                values_str += str("('") + str(routes['Name']) + str("'") +"," + str("'") +str(address) + str("'") +"," + str("'") +str(routes['EstimatedTimeOfArrivalForDisplay'])+ str("'") +"," + str("'") +str(routes['RouteSequentialPositionIndex']) + str("'") +"," + str("'") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(routes['Code']) + str("'") +"," + str("'") +str(routes['lat']) + str("'") +"," + str("'") +str(routes['lng'] ) + str("'") +"," + str("'") +str(routes['DropItems']) + str("'),")
                
                if chk_box == 0:
                    airway_bill = routes['DropItems'].split("<br>")
                    airway_bill = airway_bill[:-1]
                    
                    for airse in airway_bill:
                        airs1 = airse.split("_")
                        for airs in airs1:
                            values_box += str("('") +str(trprtid) + str("'") +"," + str("'") +str(trpsmryid) + str("'") +"," + str("'") +str(i['ID']) + str("'") +"," + str("'") +str(airs) + str("'") +"," + str("'") + str(routes['RouteSequentialPositionIndex'] -1 ) + str("'") +"," + str("'") + str(amount[airs]) + str("'),")
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
    
    except:
        pass
    
    
    
   
    
    info = {}
    info['Code'] = 'SUCCESS'
    info['IsPositive'] = 'false'
    info['message'] = ''
    info['Yield'] = result
    
    try:
        import pdb
        pdb.set_trace()
        import pymongo
        from pymongo import MongoClient
        connection = MongoClient('localhost:27017')
         
        db = connection.analytics
        collection = db.shipprtech
        result['_id'] = result['report_id']
         
        result['input_data'] = data
         
        collection.insert(result)
         
        result.pop('input_data', None)
    except:
        pass    
    
    
    return HttpResponse(json.dumps(info,) , content_type="application/json")

def GenerateSimpleBlocks(size = (55,37,30),allowed_orientation = [(1,1,1),(1,1,1),(1,1,1)],number_of_blocks = 100, container_size = (214,153,153)):
    ## length = 0, breadth = 1, height = 2
    
    
    
    
    
    
    container_length =  container_size[0]
    container_width =  container_size[1]
    container_height =  container_size[2]
    
#     for i in range(number_of_blocks):
        ## 6 orientations
    max_block = 0
    max_orientation = []
    
    ## total 6 orientation 
    for length in range(3):
        if allowed_orientation[0][length] != 0:
            
            for width in range(3):
                if width != length:
                    if allowed_orientation[1][width] != 0:
                        
                        for height in range(3):
                            if height not in [length, width]:
                                if allowed_orientation[2][height] != 0:
                                    block_length = 0
                                    block_width = 0
                                    block_height = 0
                                    nx = 0
                                    ny = 0
                                    nz = 0
                                    lengths_box = {}
                                    lengths_box["length"] = size[length]
                                    lengths_box["width"] = size[width]
                                    lengths_box["height"] = size[height]
                                    block_length += lengths_box["length"]
                                    block_width += lengths_box["width"]
                                    block_height += lengths_box["height"]
                                    while block_length <= container_length:
                                        
                                        
                                         
                                        while block_width <= container_width:
                                            
                                            
                                            while block_height <= container_height:
                                                
                                                nz += 1
                                                block_height += lengths_box["height"]
                                            
                                            ny += 1    
                                            block_width += lengths_box["width"]
                                        nx += 1
                                        block_length += lengths_box["length"]        
                                    
                                    total_block = nx*ny*nz
                                    
                                    if total_block > max_block:
                                        max_block = total_block
                                        max_orientation = [length,width,height]
                                        
                
    return   (max_block,max_orientation)      


def GenerateGeneralBlocks():
    
    allowed_orientation = [(1,1,0),(1,1,0),(1,1,1)]
    arrays = []
    import csv
    with open('gale/heavy.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            
            arrays.append([row['Length/Item\n(CM)'],row['Width/Item\n(CM)'],row['Height/Item\n(CM)'],float(row['Width/Item\n(CM)'])*float(row['Length/Item\n(CM)'])*float(row['Height/Item\n(CM)']),float(row['Weight/Item\n(KG)'])])
            
    arrays.sort(key=lambda x: x[3],reverse=True)
    arrays_list = []
    container_size = (214,153,153)
    block = {}
    i =0
    for bl in arrays:
        i += 1
        arrays_list.append(i)
        block[i] = {}
        block[i]["weight"] = float(bl[4])
        block[i]["volume"] = float(bl[3])
        block[i]["blocks"] = [i]
        j = 0
        for length in range(3):
            if allowed_orientation[0][length] != 0:
                
                for width in range(3):
                    if width != length:
                        if allowed_orientation[1][width] != 0:
                            
                            for height in range(3):
                                if height not in [length, width]:
                                    if allowed_orientation[2][height] != 0:
                                        
                                        block[i][j] = {}
                                        block[i][j][length] = {}
                                        block[i][j][length] = float(bl[0])
                                        block[i][j][width] = {}
                                        block[i][j][width] = float(bl[1])
                                        block[i][j][height] = {}
                                        block[i][j][height] = float(bl[2])
                                        block[i][j]["weight"] = float(bl[4])
                                        block[i][j]["volume"] = float(bl[3])
                                        block[i][j]["blocks"] = [i]
                                        
                                        j += 1
                                    
                                        
    P = deepcopy(block)
   
    p_keys = P.keys()
   
    N = {}
    try:
        for keys in p_keys:
            for bl_keys in block.keys():
                
                if bl_keys != keys:
                    
                    for i in P[keys].keys():
                        if i not in ["volume","weight","blocks"]:
                            for j in block[bl_keys].keys():
                                if j not in ["volume","weight","blocks"]:
                                    
                                    new_data = MergeBlock_x(bl_keys,keys, block[bl_keys][j], P[keys][i],container_size)
                                    if new_data != False:
          ## insert into new lock if its not duplicated
                                        
                                        
                                        blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
                                        if len(set(blocks)) == len(blocks):
                                            new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-x"
                                            
                                            N[new_key] = {}
                                            N[new_key]["left"] =  new_data[2]
                                            N[new_key]["right"] =  new_data[3]
                                            N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
                                            N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
                                            N[new_key][0] = new_data[2][0] + new_data[3][0]
                                            N[new_key][1] = max(new_data[2][1],new_data[3][1])
                                            N[new_key][2] = max(new_data[2][2],new_data[3][2])
                                            N[new_key]["axis"] = 0
                                            N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]
                                    new_data = MergeBlock_y(bl_keys,keys, block[bl_keys][j], P[keys][i],container_size)  
                                    if new_data != False:
                                        
                                        
                                        blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
                                        if len(set(blocks)) == len(blocks):
                                            new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-y"
                                            N[new_key] = {}
                                            N[new_key]["front"] =  new_data[2]
                                            N[new_key]["back"] =  new_data[3]
                                            N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
                                            N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
                                            N[new_key]["axis"] = 1
                                            N[new_key][0] =  max(new_data[2][0],new_data[3][0])
                                            N[new_key][1] = new_data[2][1] + new_data[3][1]
                                            N[new_key][2] = max(new_data[2][2],new_data[3][2])

                                            N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]
                                    new_data = MergeBlock_z(bl_keys,keys, block[bl_keys][j], P[keys][i],container_size)  
                                    if new_data != False:
                                        blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
                                        if len(set(blocks)) == len(blocks):
                                            new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-z"
                                            N[new_key] = {}
                                            N[new_key]["bottom"] =  new_data[2]
                                            N[new_key]["top"] =  new_data[3]
                                            N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
                                            N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
                                            N[new_key]["axis"] = 2
                                            N[new_key][0] = max(new_data[2][0],new_data[3][0])
                                            N[new_key][1] = max(new_data[2][1],new_data[3][1])
                                            N[new_key][2] = new_data[2][2] + new_data[3][2]

                                            N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]

    except:
        pass  
    
    block.update(N)
    ## blocks in N are first transferred into the set P
    P = deepcopy(N)
    p_keys = P.keys()
    
    while len(p_keys) != 0:
        
        N = {}
        for keys in p_keys:
            
            for bl_keys in block.keys():
                
                if bl_keys != keys:
                    
                    axis_chk = 0
                    try:
                        axis = block[bl_keys]['axis']
                        axis_chk = 0
                    except:
                        axis_chk = 1
                    if axis_chk == 2:
                            blocks = block[bl_keys]["blocks"] + P[keys]["blocks"]
#                             if len(set(blocks)) == len(blocks):
#                                 
#                                 new_data = MergeBlock_x(bl_keys,keys, block[bl_keys],  P[keys],container_size)
#                                 
#                                 if new_data != False:
#                                     
#                                     # remove duplicates 
#                                     
#                                         new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-x"
#                                          
#                                         N[new_key] = {}
#                                         N[new_key]["left"] =  new_data[2]
#                                         N[new_key]["right"] =  new_data[3]
#                                         N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
#                                         N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
#                                         N[new_key][0] = new_data[2][0] + new_data[3][0]
#                                         N[new_key][1] = max(new_data[2][1],new_data[3][1])
#                                         N[new_key][2] = max(new_data[2][2],new_data[3][2])
#                                         N[new_key]["axis"] = 0
#                                         N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]
#                                         
#                                 new_data = MergeBlock_y(bl_keys,keys, block[bl_keys],  P[keys],container_size) 
#                                 if new_data != False:
#                                      
#                                      
#                                     blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
#                                     if len(set(blocks)) == len(blocks):
#                                         new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-y"
#                                         N[new_key] = {}
#                                         N[new_key]["front"] =  new_data[2]
#                                         N[new_key]["back"] =  new_data[3]
#                                         N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
#                                         N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
#                                         N[new_key]["axis"] = 1
#                                         N[new_key][0] =  max(new_data[2][0],new_data[3][0])
#                                         N[new_key][1] = new_data[2][1] + new_data[3][1]
#                                         N[new_key][2] = max(new_data[2][2],new_data[3][2])
#      
#                                         N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]
#                                 new_data = MergeBlock_z(bl_keys,keys, block[bl_keys],  P[keys],container_size)
#                                 if new_data != False:
#                                     blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
#                                     if len(set(blocks)) == len(blocks):
#                                         new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-z"
#                                         N[new_key] = {}
#                                         N[new_key]["bottom"] =  new_data[2]
#                                         N[new_key]["top"] =  new_data[3]
#                                         N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
#                                         N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
#                                         N[new_key]["axis"] = 2
#                                         N[new_key][0] = max(new_data[2][0],new_data[3][0])
#                                         N[new_key][1] = max(new_data[2][1],new_data[3][1])
#                                         N[new_key][2] = new_data[2][2] + new_data[3][2]
#      
#                                         N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]

                           
                           
                    elif axis_chk == 1:
                        
                       for j in block[bl_keys].keys():
                           
                            
                            if j not in ["volume","weight","blocks"]:
                                
                                new_data = MergeBlock_x(bl_keys,keys, block[bl_keys][j],  P[keys],container_size)
                                if new_data != False:
                                    blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
                                    # remove duplicates 
                                    if len(set(blocks)) == len(blocks):
                                        new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-x"
                                        
                                        N[new_key] = {}
                                        N[new_key]["left"] =  new_data[2]
                                        N[new_key]["right"] =  new_data[3]
                                        N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
                                        N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
                                        N[new_key][0] = new_data[2][0] + new_data[3][0]
                                        N[new_key][1] = max(new_data[2][1],new_data[3][1])
                                        N[new_key][2] = max(new_data[2][2],new_data[3][2])
                                        N[new_key]["axis"] = 0
                                        N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]
                                       
                                new_data = MergeBlock_y(bl_keys,keys, block[bl_keys][j],  P[keys],container_size) 
                                if new_data != False:
                                    
                                    
                                    blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
                                    if len(set(blocks)) == len(blocks):
                                        new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-y"
                                        N[new_key] = {}
                                        N[new_key]["front"] =  new_data[2]
                                        N[new_key]["back"] =  new_data[3]
                                        N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
                                        N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
                                        N[new_key]["axis"] = 1
                                        N[new_key][0] =  max(new_data[2][0],new_data[3][0])
                                        N[new_key][1] = new_data[2][1] + new_data[3][1]
                                        N[new_key][2] = max(new_data[2][2],new_data[3][2])

                                        N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]
                                new_data = MergeBlock_z(bl_keys,keys, block[bl_keys][j],  P[keys],container_size)
                                if new_data != False:
                                    blocks = new_data[2]["blocks"] + new_data[3]["blocks"]
                                    if len(set(blocks)) == len(blocks):
                                        
                                        new_key = str(new_data[0]) + "-" + str(new_data[1]) + "-z"
                                        N[new_key] = {}
                                        N[new_key]["bottom"] =  new_data[2]
                                        N[new_key]["top"] =  new_data[3]
                                        N[new_key]["weight"] = new_data[2]["weight"] + new_data[3]["weight"]
                                        N[new_key]["volume"] = new_data[2]["volume"] + new_data[3]["volume"]
                                        N[new_key]["axis"] = 2
                                        N[new_key][0] = max(new_data[2][0],new_data[3][0])
                                        N[new_key][1] = max(new_data[2][1],new_data[3][1])
                                        N[new_key][2] = new_data[2][2] + new_data[3][2]

                                        N[new_key]["blocks"] = new_data[2]["blocks"] + new_data[3]["blocks"]

                       
                     
        block.update(N)
    ## blocks in N are first transferred into the set P
        P = deepcopy(N)
        p_keys = P.keys()        
    blk_itm = block.items()
    blk_itm.sort(key=lambda x: x[1]['volume'],reverse = True)
    space = [[[0,0,0], container_size]]
    
    generate_freespace(blk_itm,space,container_size,arrays_list)
               
                                       
#                         do it same for y axis
#                         do it for z axis(check for height anf over balncing)s
       
       
## empty space Node
class SpaceNode(object):
    def __init__(self, origin=None, top=None, root = None,linked_list = []):
        
        self.origin = origin
        self.upper_origin = top 
        self.root = root
        self.linked_list = []
class BoxNode(object):
    def __init__(self, origin=None, top=None, desc = None):
        
        self.origin = origin
        self.upper_origin = top 
        self.desc = desc
        
        

#     def get_data(self):
#         return self.data
# 
#     def get_next(self):
#         return self.linked_node
# 
#     def set_next(self, new_next):
#         self.linked_node = new_next
                                     
    
def cluster():
    
    import csv
    array = []
    with open('gale/heavy.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            
            array.append([row['Length/Item\n(CM)'],row['Width/Item\n(CM)'],row['Height/Item\n(CM)'],float(row['Width/Item\n(CM)'])*float(row['Length/Item\n(CM)'])*float(row['Height/Item\n(CM)']),float(row['Weight/Item\n(KG)'])])
            
    from sklearn.cluster import KMeans
    model = KMeans(n_clusters = 10)
    model.fit(array)
    label = model.predict(array)
    print label
    import matplotlib
   
    import matplotlib.pyplot as plt
    xs = array[:,0]
    ys = array[:,2]
    plt.scatter(xs,ys,c = labels)
    plt.show()
    
def comp_vol(space):
    final_volume = 0
    
    for v in space:
        volume = 1
        for i in range(0,3):
            
            ## volume for free space
            volume *= (v.upper_origin[i] - v.origin[i])
            
        final_volume += volume
    return final_volume
def generate_space_nodes(box_b_dimension,space):
    '''   space linked list node    '''
    
    final_space = []
    space_dims = []
    for i in range(0,3):
        space_dim = space.upper_origin[i] - space.origin[i]
        space_dims.append(space_dim)
    t = 0
    for i in range(0,3):
       
        diff_dim = space_dims[i] - box_b_dimension[i]
        if diff_dim > 0:
            
            if i == 0:
                origin = (space.origin[0] + diff_dim,space.origin[1],space.origin[2])
                upper_origin = space.upper_origin
                new_node = SpaceNode(origin,upper_origin)
                final_space.append(new_node)
                t += 1 
                
            elif i == 1:
                origin = (space.origin[0] ,space.origin[1]+ diff_dim,space.origin[2])
                upper_origin = space.upper_origin
                if t > 0:
                    
                    new_node = SpaceNode(origin,upper_origin,new_node)
                else:
                    new_node = SpaceNode(origin,upper_origin)
                final_space.append(new_node)
                    
                
            elif i == 2:
                origin = (space.origin[0] ,space.origin[1],space.origin[2]+ diff_dim)
                upper_origin = space.upper_origin
                if t > 0:
                    
                    new_node = SpaceNode(origin,upper_origin,new_node)
                else:
                    new_node =  SpaceNode(origin,upper_origin)
                final_space.append(new_node)
    for i in final_space:
        i.linked_list = final_space
    return  final_space
        
def check_z_constraint(space,used_boxes):
    import pdb
    pdb.set_trace()

''' disection of space '''
def space_dissect(space,box_b_dimension,used_boxes):
    space_nodes = []
    
    
    for i in space:
        if i.origin[2] != 0:
            chk_constraint = check_z_constraint(i,used_boxes)
            
        if box_b_dimension[0] >= i.origin[0] and  box_b_dimension[0] <= i.upper_origin[0]:
             if box_b_dimension[1] >= i.origin[1] and  box_b_dimension[1] <= i.upper_origin[1]:
                  if box_b_dimension[2] >= i.origin[2] and  box_b_dimension[2] <= i.upper_origin[2]:
                    
                    empty_spaces = generate_space_nodes(box_b_dimension,i)
                    box = BoxNode(i.origin,box_b_dimension)
                    space_nodes = [box,empty_spaces]
    return space_nodes

                
def manhattan_dist(first,second):
    dist = 0
    
    for i in range(0,3):
        dist += abs(first[i] - second[i])
    return dist
def find_anchor(space, container_size):
    min_dis = -1
    anchor_corner = -1
    new_space = []
    new_space.append(space.origin)
    new_space.append(space.upper_origin)
    for i in range(0,2):
        for j in range(0,2):
            for k in range(0,2):
                
                
                space_dim = (new_space[i][0], new_space[j][1], new_space[k][2])
                for size in container_size:
                    if min_dis == -1:
                        min_dis = manhattan_dist(size,space_dim)
                        anchor_corner = size
                    else:
                        temp_dis = manhattan_dist(size,space_dim)
                        if min_dis > temp_dis:
                            min_dis = temp_dis
                            anchor_corner = size
                    if  min_dis == 0:
                        
                        return(min_dis,anchor_corner)       
    return(min_dis,anchor_corner)
    
    
    
            
                
def form_corner(container_size):
    container_list = []
    container_list.append((0,0,0))
    container_list.append(container_size)
    corners = []
    
        
    for i in range(0,2):
        for j in range(0,2):
            for k in range(0,2):
                new_array = []
                new_array.append(container_list[i][0])
                new_array.append(container_list[j][1])
                new_array.append(container_list[k][2])
                
                corners.append(new_array)
    
    return corners
    
    
    
def selected_space_list(space_list, container_size):
    selected_space = []
    anchor_dist_comp = -1
    for i in space_list:
        
        anchor_dist,anchor = find_anchor(i,container_size)  
          
        if anchor_dist_comp == -1:
            selected_space = [i]
            anchor_dist_comp = anchor_dist
        elif anchor_dist_comp == anchor_dist :
            selected_space.append(i)
        elif anchor_dist_comp > anchor_dist :
            selected_space = [i]
            anchor_dist_comp = anchor_dist
    return selected_space
''' generate free space '''    
def generate_freespace(box_b_list, space,container_size,arrays_list):
    new_space_list = []
    cont_vol = container_size[0]*container_size[1]*container_size[2]
    container_corner = form_corner(container_size)
    ''' create space node '''
    sp_nd = SpaceNode(space[0][0],space[0][1])
    space = [sp_nd]
    space_resused = True
    used_boxes = []
    for ik in box_b_list:
        print ik[0],ik[1]["volume"]
    while space_resused != False:
        already_used  = set()
        for box_b in box_b_list:
            
            box_volume = box_b[1]['volume']
#             space_vol = comp_vol(space)
#             if space_vol ==  box_volume:
#                 return 
            
            if already_used.intersection(set(box_b[1]['blocks'])) == set([]):
                
                selected_space = selected_space_list(space, container_corner)
                box_b_key = box_b[0]
                '''cordinated to be find '''
                
                space = set(space).difference(set(selected_space))
                box_b_dimension =  (box_b[1][0],box_b[1][1],box_b[1][2])
                
                
                result = space_dissect(selected_space,box_b_dimension,used_boxes)
                
                
                space.update(result[1])
               
                already_used = already_used.union(set(box_b[1]["blocks"]))
                result[0].desc = box_b
                
                used_boxes.append(result[0])
                
                
        
def chk_volume(first_block, second_block,container_size,axis = 0):
        if axis == 0:
            block_len = first_block[0]+ second_block[0]
            block_breadth = max(first_block[1],second_block[1])
            block_height = max(first_block[2],second_block[2])
            
        elif axis == 1:
            block_len = max(first_block[0],second_block[0])
            block_breadth = first_block[1]+ second_block[1]
            block_height = max(first_block[2],second_block[2])
           
        else:
            block_len = max(first_block[0],second_block[0])
            block_breadth = max(first_block[1],second_block[1])
            block_height = first_block[2]+ second_block[2]
            
        if block_len > container_size[0]:
            return False
        if block_breadth > container_size[1]:
            return False
        if block_height > container_size[2]:
            return False
            
        envolope_volume = (block_len)*(block_breadth)*(block_height)
        
        total_volume = first_block["volume"] + second_block["volume"]
        
        if total_volume/envolope_volume >= .98:
            return True
        else:
            return False
                                    


def MergeBlock_x(first_original_block, second_original_block,first_block, second_block,container_size):
    left_block = 0
    right_block = 0
    left_orig = 0
    right_orig = 0
    parm_chk = 0
    try:
        if first_block[1]*first_block[2] >= second_block[1]*second_block[2]:
            if first_block[1] >= second_block[1]:
                if chk_volume(first_block, second_block,container_size,0) == True:
                    left_block = first_block
                    right_block = second_block
                    left_orig = first_original_block
                    right_orig = second_original_block
                    
                    parm_chk = 1
    except:
        import pdb
        pdb.set_trace()
    
    if parm_chk == 0:
        if first_block[1]*first_block[2] <= second_block[1]*second_block[2]:
            if first_block[1] <= second_block[1]:
                if chk_volume(first_block, second_block,container_size,0) == True:
                    left_block = second_block
                    right_block = first_block
                    left_orig = second_original_block
                    right_orig = first_original_block
                    parm_chk = 1
                    
                
                
    
    if parm_chk == 0:
        return False
    else:
        
        return(left_orig,right_orig, left_block,right_block)

def MergeBlock_y(first_original_block, second_original_block,first_block, second_block,container_size):
    left_block = 0
    right_block = 0
    left_orig = 0
    right_orig = 0
    parm_chk = 0
    
    if first_block[0]*first_block[2] >= second_block[0]*second_block[2]:
        if first_block[0] >= second_block[0]:
            if chk_volume(first_block, second_block,container_size,1) == True:
                left_block = first_block
                right_block = second_block
                left_orig = first_original_block
                right_orig = second_original_block
                
                parm_chk = 1
    if parm_chk == 0:
        if first_block[0]*first_block[2] <= second_block[0]*second_block[2]:
            if first_block[0] <= second_block[0]:
                if chk_volume(first_block, second_block,container_size,1) == True:
                    left_block = second_block
                    right_block = first_block
                    left_orig = second_original_block
                    right_orig = first_original_block
                    parm_chk = 1
                    
                
                
    
    if parm_chk == 0:
        return False
    else:
        
        return(left_orig,right_orig, left_block,right_block)


def MergeBlock_z(first_original_block, second_original_block,first_block, second_block,container_size):
    left_block = 0
    right_block = 0
    left_orig = 0
    right_orig = 0
    parm_chk = 0
    
    
    if first_block[0] >= second_block[0] and first_block[1] >= second_block[1]:
        if chk_volume(first_block, second_block,container_size,2) == True:
            left_block = first_block
            right_block = second_block
            left_orig = first_original_block
            right_orig = second_original_block
            parm_chk = 1
    if parm_chk == 0:
        
        if first_block[0] <= second_block[0] and first_block[1] <= second_block[1]:
            if chk_volume(first_block, second_block,container_size,2) == True:
                left_block = second_block
                right_block = first_block
                left_orig = second_original_block
                right_orig = first_original_block
                parm_chk = 1
                    
                
                
    
    if parm_chk == 0:
        return False
    else:
        
        return(left_orig,right_orig, left_block,right_block)

def checkspace_util(block1, block2):
    return block1, block2







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
    
    