import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

import threading
import requests

def distance(input):
    lat1 = input[0]
    lon1 = input[1]
    lat2 = input[2]
    lon2 = input[3]
    import json
    import urllib
    import googlemaps
    gmaps = googlemaps.Client(key='AIzaSyBOp8MtZAS5SHVzZFdWB-5kmG3OVwycT5o')
    location1 = lat1,lon1
    location2 = lat2,lon2
    
    result = gmaps.distance_matrix(location1, location2, mode='driving')
   
    driving_distance = result['rows'][0]['elements'][0]['distance']['value']
    
    
    driving_distance =  float(driving_distance)/float(1000)
    return driving_distance


def distance_new_key(input):
    lat1 = input[0]
    lon1 = input[1]
    lat2 = input[2]
    lon2 = input[3]
    import json
    import urllib
    import googlemaps
    gmaps = googlemaps.Client(key='AIzaSyA0tV1u4U11pOb82kXrqrVI0YtT5neutGg')
    location1 = lat1,lon1
    location2 = lat2,lon2
    
    result = gmaps.distance_matrix(location1, location2, mode='driving')
   
    driving_distance = result['rows'][0]['elements'][0]['distance']['value']
    
    
    driving_distance =  float(driving_distance)/float(1000)
    return driving_distance


def distance_osrm(input):
    lat1 = input[0]
    lon1 = input[1]
    lat2 = input[2]
    lon2 = input[3]
    osrm_url = "http://localhost:5000/route/v1/driving/"
    url = osrm_url + str(lon1) + str(",") + str(lat1) + str(";") + str(lon2) + str(",") + str(lat2)
    params = {'alternatives': 'true', 'geometries':'geojson'}
    results = requests.get(url, params=params).json()['routes']
    distance = round((float(results[0]['distance'])/1000),2)
    
    return distance  

def distance1(input):
    lat1 = input[0]
    lon1 = input[1]
    lat2 = input[2]
    lon2 = input[3]
    
    
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
    
    return float(dist)







       
# def parallel_dist(input):
#     
# #     import pdb
# #     pdb.set_trace()
# #     x1 = locations[from_node][0]
# #     y1 = locations[from_node][1]
# #     x2 = locations[to_node][0]
# #     y2 = locations[to_node][1]
# #     self.matrix[from_node][to_node] = distance(x1, y1, x2, y2)


# Distance callback

class CreateDistanceCallback(object):
  """Create callback to calculate distances and travel times between points."""

  
  
  
  
  
  def __init__(self, locations):
    """Initialize distance array."""
    self.matrix = {}
    
    def matrix(cordinates):
    
        try:
            self.matrix[cordinates[1]][cordinates[2]] = self.matrix[cordinates[2]][cordinates[1]]  
        
        except:
        ##  if we need to change to osrm point to distance osrm
            self.matrix[cordinates[1]][cordinates[2]] = distance1(cordinates[3:])

    import  datetime    
    
    from multiprocessing.dummy import Pool as ThreadPool 
    
    
    pool = ThreadPool(8)
    cd = []
#     create_workers()
    num_locations = len(locations)
    
    
    for from_node in xrange(num_locations):
      self.matrix[from_node] = {}
      for to_node in xrange(num_locations):
          
        
        x1 = locations[from_node][0]
        y1 = locations[from_node][1]
        x2 = locations[to_node][0]
        y2 = locations[to_node][1]
        cordinates = [1,from_node,to_node,x1,y1,x2,y2]
#         matrix(cordinates)
        cd.append(cordinates)
    pool = ThreadPool(16) 
    results = pool.map(matrix, cd)
    pool.close() 
    pool.join()#        cd.append(cordinates)
#    pool = ThreadPool(4) 
#    results = pool.map(matrix, cd)
#    pool.close() 
#    pool.join()
#      
#         try:
#             self.matrix[cordinates[1]][cordinates[2]] = self.matrix[cordinates[2]][cordinates[1]]  
#         
#         except:
#         
#             self.matrix[cordinates[1]][cordinates[2]] = distance_osrm(cordinates[3:])
#         work_temp([len(cd),from_node,to_node,x1,y1,x2,y2])
#         if distance1([x1,y1,x2,y2]) > 40:
#             print x1,y1,x2,y2,distance1([x1,y1,x2,y2])
#         
#         queue.put([len(cd),from_node,to_node,x1,y1,x2,y2])
#     queue.join()   
#           
     
#         self.matrix[from_node][to_node] = distance1([x1,y1,x2,y2])
        
    
    

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


class   CreateAfterCostCallback():
 
    def __init__(self):
        
        self.matrix = {}
 
    def calculate(self, to_node,vehicle):
        if to_node == 0:
            return 0
        else:
            try:
                
                ls = self.matrix[vehicle]
                ls.append(to_node)
                ls = list(set(ls))
                
                self.matrix[vehicle] = ls
            except:
                self.matrix[vehicle] =[to_node]
            if len(self.matrix[vehicle]) > 20:
                return 1000
            else:
                return 0



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
def main(data,truck_options):
  # Create the data.
  
#   data = create_data_array()
 
  locations = data[0]
  demands = data[1]
  start_times = data[2]
  end_times = data[3]
  volume = data[4]
  address = data[5]
  nodes = data[6]
  num_locations = len(locations)
  depot = 0
  
  try:
      
    num_vehicles = 20
  except:
    num_vehicles = 100
  search_time_limit = 400000
 

  # Create routing model.
  if num_locations > 0:

    # The number of nodes of the VRP is num_locations.
    # Nodes are indexed from 0 to num_locations - 1. By default the start of
    # a route is node 0.
    

    # Callbacks to the distance function and travel time functions here.
    
    dist_between_locations = CreateDistanceCallback(locations)
    
#     dist_between_locations.matrix = matrix
    dist_callback = dist_between_locations.Distance
    
#     routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
    demands_at_locations = CreateDemandCallback(demands)
    demands_callback = demands_at_locations.Demand
    VehicleCapacity = []
    VolumeCapacity = []
    selected_cost = []
    for i in  truck_options['SelectedDeliveryVehicles']:
        if i['Code'] == 'V400':
            VehicleCapacity.append(int(i['WeightAllowed']))
             
            VolumeCapacity.append(1345)
            selected_cost.append(1200)
            selected_vehicle = i
    
        if i['Code'] == 'V500':
                VehicleCapacity.append(int(i['WeightAllowed']))
             
                VolumeCapacity.append(int(i['VmWtAllowed']))
                selected_cost.append(4750)
                selected_vehicle = i
#     if VehicleCapacity == 0:
#         for i in  truck_options['SelectedDeliveryVehicles']:
#             if i['Code'] == 'V200':
#                 VehicleCapacity = int(i['WeightAllowed'])
#                  
#                 VolumeCapacity = int(i['VmWtAllowed'])
#                 selected_vehicle = i 

    
    if VehicleCapacity == []:
        VehicleCapacity.append(750)
             
        VolumeCapacity.append(983)
        selected_cost.append(1200)
        selected_vehicle = "i"
    
    capacity = []
    cost = []
    k = 0
    volumetric = []
    for i in range(num_vehicles/len(VehicleCapacity)):
        for j in range(len(VehicleCapacity)):
        
            
            capacity.append(VehicleCapacity[j])
            volumetric.append(VolumeCapacity[j])
            cost.append(selected_cost[j])
        
#             k += 1
            
    
    num_vehicles = len(capacity)
    routing = pywrapcp.RoutingModel(num_locations, num_vehicles, depot)
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    maximum_dist = int(truck_options['MaxDistancePerVehicle'])
    NullDistanceStack = 0
    fix_start_cumul_to_zero = True
    distance_check = "Distances"
    routing.AddDimension(dist_callback, NullDistanceStack, maximum_dist,
                         fix_start_cumul_to_zero, distance_check)
    NullCapacitySlack = 0
    
    routing.AddDimensionWithVehicleCapacity(
      demands_callback,  # demand callback
      NullCapacitySlack,
      capacity,  # capacity array
      True,
      'Capacity')
    
    volume_at_locations = CreateVolumeCallback(volume)
    volume_callback = volume_at_locations.Volume
    routing.AddDimensionWithVehicleCapacity(
      volume_callback,  # demand callback
      NullCapacitySlack,
      volumetric,  # capacity array
      True,
      'CapacityVolume')
    distance_dimension = routing.GetDimensionOrDie(distance_check)
    

  # Set vehicle costs for each vehicle, not homogenious.
    
         
    
    # Adding capacity dimension constraints.
    

    

    
    
    
      
    
    fix_start_cumul_to_zero = True
    capacity = "Capacities"
    routing.AddDimension(demands_callback, NullCapacitySlack, max(VehicleCapacity),
                         fix_start_cumul_to_zero, capacity)
#     
    
    
    
        
    ## Adding Volume constraint
   
    
     
    NullVolumeSlack = 0;
    fix_start_cumul_to_zero = True
    volumes = "Volume"

    routing.AddDimension(volume_callback, NullVolumeSlack, max(VolumeCapacity),
                         fix_start_cumul_to_zero, volumes)
    
    
    
    
    # Add time dimension.
    
    time_per_demand_unit =  int(truck_options['MHaltTimeAtDropPoint'])*60
    horizon = 24 * 3600
    time = "Time"
    speed = int(truck_options['AverageSpeedOfVehicle'])
    
    service_times = CreateServiceTimeCallback(demands, time_per_demand_unit)
    service_time_callback = service_times.ServiceTime

    travel_times = CreateTravelTimeCallback(dist_callback, speed)
    travel_time_callback = travel_times.TravelTime

    total_times = CreateTotalTimeCallback(service_time_callback, travel_time_callback)
    total_time_callback = total_times.TotalTime
    duration = end_times[0] - start_times[0]
    routing.AddDimension(total_time_callback,  # total time function callback
                         horizon,
                         duration,
                         False,
                         time)
    # Add time window constraints.
    time_dimension = routing.GetDimensionOrDie(time)
    
    for location in range(1, num_locations):
      
      start = start_times[location] - start_times[0]
      end = start + end_times[location] - start_times[location] 
        
      location_idx = routing.NodeToIndex(location)
      time_dimension.CumulVar(location_idx).SetRange(start, end)
      
      routing.AddToAssignment(time_dimension.SlackVar(location_idx))
    cost_after_lcoations = CreateAfterCostCallback()
    cost_after_callback = cost_after_lcoations.calculate
    vehicle_call_backs = [lambda i, j: cost_after_callback(j, vehicle) for vehicle in range(num_vehicles)]
    

#         routing.SetVehicleCost(int(veh), vehicle_call_backs_cost[veh])  
       
        
        
    for vehicle_id in xrange(num_vehicles):
        index = routing.Start(vehicle_id)
#         routing.SetFixedCostOfVehicle(cost[vehicle_id], int(vehicle_id)) 
        
        
        
#         distance_dimension.CumulVar(index)
#         distance_dimension.SetSpanCostCoefficientForVehicle(cost[vehicle_id],vehicle_id)
        routing.SetArcCostEvaluatorOfVehicle(vehicle_call_backs[vehicle_id], vehicle_id) 
        time_dimension.CumulVar(index).SetRange(0,duration)
        routing.AddToAssignment(time_dimension.SlackVar(index))
     
    # Solve displays a solution if any.
    
    #     search_parameters.time_limit_ms = 30000
#     search_parameters.solution_limit = 100
#     
    
    assignment = routing.SolveWithParameters(search_parameters)
    if assignment:
      
      size = len(locations)
      # Solution cost.
      
#       print "Total distance of all routes: " + str(assignment.ObjectiveValue()) + "\n"
      # Inspect solution.
      capacity_dimension = routing.GetDimensionOrDie(capacity);
      time_dimension = routing.GetDimensionOrDie(time);
      volume_dimension = routing.GetDimensionOrDie(volumes);
      distance_dimension = routing.GetDimensionOrDie(distance_check);
      plans = []
      
      distances = []
      cum_distance = []
      address1 = []
      truck = []
      
      volume1 = []
      cum_volume = []
      time_range = []
      weight = []
      cum_weight = []
      
      for vehicle_nbr in range(num_vehicles):
        index = routing.Start(vehicle_nbr)
        plan_output = 'Route {0}:'.format(vehicle_nbr)
        plan1 = []
        dist = 0
        number_del = 0
        
        while not routing.IsEnd(index):
          
          node_index = routing.IndexToNode(index)
          
          
          
          
          
          number_del += 1
          if node_index == 0:
              node_prev = 0
              dist += 0
              dist1 = 0
          else:
              
              dist1 =  dist_between_locations.matrix[node_index][node_prev]      
              dist += dist1
              node_prev = node_index
          distances.append(dist1)
          cum_distance.append(dist)
          address1.append(address[node_index])
          truck.append("Truck" + str(vehicle_nbr+1))
          weight.append(demands[node_index])
          
          volume1.append(volume[node_index])
          dist_var = distance_dimension.CumulVar(index)
          load_var = capacity_dimension.CumulVar(index)
          vol_var = volume_dimension.CumulVar(index)
          time_var = time_dimension.CumulVar(index)
          cum_weight.append(assignment.Value(load_var))
          cum_volume.append(assignment.Value(vol_var))
          time_range.append(str(assignment.Min(time_var))+ " - " + str(assignment.Max(time_var)))
          plan1.append((nodes[node_index],dist1,assignment.Value(load_var),assignment.Value(vol_var),str(assignment.Min(time_var) + start_times[0]),str(assignment.Max(time_var) + start_times[0]),locations[node_index],node_index))
          plan_output += \
                    " {node_index} Load({load}) Vol({vol}) Dist({dist}) Time({tmin}, {tmax}) -> ".format(
                        node_index=node_index,
                        load=assignment.Value(load_var),
                        vol = assignment.Value(vol_var),
                        dist = dist,
                        tmin=str(assignment.Min(time_var)),
                        tmax=str(assignment.Max(time_var)))
          index = assignment.Value(routing.NextVar(index))
        
        node_index = routing.IndexToNode(index)
        
        dist1 =  dist_between_locations.matrix[node_index][node_prev]   
        dist += dist1
        node_prev = node_index
        distances.append(dist1)
        cum_distance.append(dist)
        address1.append(address[node_index])
        truck.append("Truck" + str(vehicle_nbr+1))
        weight.append(demands[node_index])
        volume1.append(volume[node_index])
        dist_var = distance_dimension.CumulVar(index)
        load_var = capacity_dimension.CumulVar(index)
        vol_var = volume_dimension.CumulVar(index)
        time_var = time_dimension.CumulVar(index)
        cum_weight.append(assignment.Value(load_var))
        cum_volume.append(assignment.Value(vol_var))
        time_range.append(str(assignment.Min(time_var))+ " - " + str(assignment.Max(time_var)))

        plan1.append((nodes[node_index],dist1,assignment.Value(load_var),assignment.Value(vol_var),str(assignment.Min(time_var) + start_times[0]),str(assignment.Max(time_var) + start_times[0]),locations[node_index],node_index))

        plan_output += \
                  " {node_index} Load({load}) Vol({vol}) Dist({dist}) Time({tmin}, {tmax})".format(
                      node_index=node_index,
                      load=assignment.Value(load_var),
                      vol = assignment.Value(vol_var),
                      dist = dist,
                      tmin=str(assignment.Min(time_var)),
                      tmax=str(assignment.Max(time_var)))
#         print plan_output
#           
#         print "\n"
#         print dist, number_del
#         print "\n"
        if len(plan1) == 2 and plan1[1][0] == 0:
            pass
        else:    
            plans.append(plan1)
        
    else:
      print 'No solution found.'
  else:
    print 'Specify an instance greater than 0.'
  
  return (plans,selected_vehicle) 

def create_data_array():

    import csv
    locations = []
    locations.append([12.844123, 77.682088])
    
    demands=  []
    demands.append(float(0))
    
    locations1 = []
    address = []
    address.append("Gopalan gardenia, Veerasandra Main Rd, BTM Phase 1, Veer Sandra, Electronic City, Bengaluru, Karnataka 560100")
    volume = []
    volume.append(float(0))
    
    with open('gale/BLRY/result_20_04.csv') as csvfile:
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
    
    print len(locations), sum(demands),sum(volume),len(address)
    
    
    
    start_times =  [0] * len(locations)
    
    # tw_duration 43200is the width of the time windows.
    tw_duration = 38200
    
    # In this example, the width is the same at each location, so we define the end times to be
    # start times + tw_duration. For problems in which the time window widths vary by location,
    # you can explicitly define the list of end_times, as we have done for start_times.
    end_times = [0] * len(start_times)
    
    for i in range(len(start_times)):
      end_times[i] = start_times[i] + tw_duration
    
    data = [locations, demands, start_times, end_times,volume,address]
    
    return data
def create_temp():
    import analyze  
    data = analyze.data()
    info = data[1]
    route = data[0]
    keys = route.keys()
    start_times = []
    track_key = []
    volume = []
    routes = []
    locations = []
    demands = []
    address = []
    for i2 in range(len(keys)):
        final_data = route[keys[i2]]
        

        for i in final_data:
            
            row = info[i[0]]
            volume_ind = float(row['Length'])*float(row['Height'])*float(row['Height'])
            ind = row['location'].index(",")
            
            check = row['ADDRESS']
            if check in address:
                ind = address.index(check)
                if keys[i2] != routes[i2]:
                    import pdb
                    pdb.set_trace()
                demands[ind] = demands[ind] + float(row['Weight'])
                volume[ind] = volume[ind] + volume_ind
                
                
            else:
                routes.append(keys[i2])
                track_key.append(i[0])
                locations.append([float(row['location'][1:ind]),float(row['location'][ind+1:-1])])     
                demands.append(float(row['Weight']))   
                address.append(row['ADDRESS'])    
                volume.append(volume_ind)
        print keys[i2]
        print len(locations), sum(demands),sum(volume),len(address)
    data = []
#     start_times =  [0] * len(locations)
#     tw_duration = 37800
#     end_times = [0] * len(start_times)
#     for i in range(len(start_times)):
#         end_times[i] = start_times[i] + tw_duration
#     
#     data = [locations, demands, start_times, end_times,volume,address]
    return data
if __name__ == '__main__':
  main()