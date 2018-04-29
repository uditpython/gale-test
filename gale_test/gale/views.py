# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import threading
import requests
import time
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from gale_test.settings import NUMBER_OF_THREADS
import queue as Queue

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
    with open('/Users/Deepak/git/gale-test/gale_test/gale/output_new.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
               
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
        if data_new != None:
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


def route(request):
    
    import rt1
    data = rt1.main()
   
    label = 'Truck'
    
    info = {}
    for i in range(len(data)):
        truck_data = []
        for j in range(1,len(data[i])):
            
            truck_data.append(data[i][j][5])
        info[label+str(i+1)] = truck_data
    
        
    return HttpResponse(json.dumps(info) , content_type="application/json")




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
    
    