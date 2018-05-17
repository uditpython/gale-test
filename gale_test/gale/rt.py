import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2



# def distance1(lat1, lon1, lat2, lon2):
#     import json
#     import urllib
#     import googlemaps
#     gmaps = googlemaps.Client(key='AIzaSyBOtRLrxD2JLwjM5_7Z8iFRCYHbpdQrvjo')
#     location1 = lat1,lon1
#     location2 = lat2,lon2
#     result = gmaps.distance_matrix(location1, location2, mode='transit')
#     driving_distance = result['rows'][0]['elements'][0]['distance']['value']
#     driving_distance = driving_distance/1000
#     print driving_distance,distance1(lat1, lon1, lat2, lon2)
#     return driving_distance




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
    print(dist)
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
def main():
  # Create the data.

  data = create_data_array()
  locations = data[0]
  demands = data[1]
  start_times = data[2]
  end_times = data[3]
  volume = data[4]
  address = data[5]
  parent_order = data[6]
  order_list = data[7]
  route_grof =data[8]
  new_address = data[9]
  num_locations = len(locations)
  depot = 0
  num_vehicles = 17
  search_time_limit = 400000

  # Create routing model.
  if num_locations > 0:

    # The number of nodes of the VRP is num_locations.
    # Nodes are indexed from 0 to num_locations - 1. By default the start of
    # a route is node 0.
    routing = pywrapcp.RoutingModel(num_locations, num_vehicles, depot)
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()

    # Callbacks to the distance function and travel time functions here.
    dist_between_locations = CreateDistanceCallback(locations)
    dist_callback = dist_between_locations.Distance

    routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
    demands_at_locations = CreateDemandCallback(demands)
    demands_callback = demands_at_locations.Demand



    maximum_dist = 100
    NullDistanceStack = 0
    fix_start_cumul_to_zero = True
    distance_check = "Distances"
    routing.AddDimension(dist_callback, NullDistanceStack, maximum_dist,
                         fix_start_cumul_to_zero, distance_check)




    # Adding capacity dimension constraints.
    VehicleCapacity = 750
    NullCapacitySlack = 0
    fix_start_cumul_to_zero = True
    capacity = "Capacity"
    routing.AddDimension(demands_callback, NullCapacitySlack, VehicleCapacity,
                         fix_start_cumul_to_zero, capacity)



    ## Adding Volume constraint
    volume_at_locations = CreateVolumeCallback(volume)
    volume_callback = volume_at_locations.Volume

    VolumeCapacity = 10607700000;
    NullVolumeSlack = 0;
    fix_start_cumul_to_zero = True
    volumes = "Volume"

    routing.AddDimension(volume_callback, NullVolumeSlack, VolumeCapacity,
                         fix_start_cumul_to_zero, volumes)




    # Add time dimension.
    time_per_demand_unit = 1200
    horizon = 24 * 3600
    time = "Time"
    speed = 30

    service_times = CreateServiceTimeCallback(demands, time_per_demand_unit)
    service_time_callback = service_times.ServiceTime

    travel_times = CreateTravelTimeCallback(dist_callback, speed)
    travel_time_callback = travel_times.TravelTime

    total_times = CreateTotalTimeCallback(service_time_callback, travel_time_callback)
    total_time_callback = total_times.TotalTime

    routing.AddDimension(total_time_callback,  # total time function callback
                         horizon,
                         horizon,
                         fix_start_cumul_to_zero,
                         time)
    # Add time window constraints.
    time_dimension = routing.GetDimensionOrDie(time)
    for location in range(1, num_locations):

      start = start_times[location]
      end = end_times[location]
      time_dimension.CumulVar(location).SetRange(start, end)
    # Solve displays a solution if any.

#     search_parameters.time_limit_ms = 30000
#     search_parameters.solution_limit = 100
#
    assignment = routing.SolveWithParameters(search_parameters)
    if assignment:

      size = len(locations)
      # Solution cost.

      print "Total distance of all routes: " + str(assignment.ObjectiveValue()) + "\n"
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


      parent_orders = []
      order_lists = []
      route_grofs = []

      new_addresss = []

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

              dist1 =  distance(locations[node_prev][0], locations[node_prev][1], locations[node_index][0], locations[node_index][1])
              dist += dist1
              node_prev = node_index
          distances.append(dist1)
          cum_distance.append(dist)
          address1.append(address[node_index])
          parent_orders.append(parent_order[node_index])
          order_lists.append(order_list[node_index])
          route_grofs.append(route_grof[node_index])

          try:
              new_addresss.append(new_address[node_index])
          except:
               new_addresss.append(new_address[node_index - 1])
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
          plan1.append((node_index,assignment.Value(load_var),assignment.Value(vol_var),str(assignment.Min(time_var)),str(assignment.Max(time_var)),locations[node_index]))
          plan_output += \
                    " {node_index} Load({load}) Vol({vol}) Dist({dist}) Time({tmin}, {tmax}) -> ".format(
                        node_index=node_index,
                        load=assignment.Value(load_var),
                        vol = assignment.Value(vol_var),
                        dist = assignment.Value(dist_var),
                        tmin=str(assignment.Min(time_var)),
                        tmax=str(assignment.Max(time_var)))
          index = assignment.Value(routing.NextVar(index))

        node_index = routing.IndexToNode(index)

        dist1 =  distance(locations[node_prev][0], locations[node_prev][1], locations[node_index][0], locations[node_index][1])
        dist += dist1
        node_prev = node_index
        distances.append(dist1)
        cum_distance.append(dist)
        address1.append(address[node_index])
        parent_orders.append(parent_order[node_index])
        order_lists.append(order_list[node_index])
        route_grofs.append(route_grof[node_index])
        new_addresss.append(new_address[node_index])



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

        plan1.append((node_index,assignment.Value(load_var),assignment.Value(vol_var),str(assignment.Min(time_var)),str(assignment.Max(time_var)),locations[node_index]))

        plan_output += \
                  " {node_index} Load({load}) Vol({vol}) Dist({dist} Time({tmin}, {tmax})".format(
                      node_index=node_index,
                      load=assignment.Value(load_var),
                      vol = assignment.Value(vol_var),
                      dist = assignment.Value(dist_var),
                      tmin=str(assignment.Min(time_var)),
                      tmax=str(assignment.Max(time_var)))
        print plan_output
        import pandas
        df = pandas.DataFrame(data={"Truck": truck, "Address": address1,"New Address":new_addresss,"distance":distances,"cum_distance":cum_distance,"weight":weight,"cum_weight": cum_weight, "volume":volume1,"cum_vol":cum_volume,"time_range":time_range,'parent_order':parent_orders,'order_list':order_lists,'Route GRof':route_grofs})
#         df.to_csv('gale/result_routes_new31.csv', index=False)
        print "\n"
        print dist, number_del
        print "\n"
        if len(plan1) == 2 and plan1[1][0] == 0:
            pass
        else:
            plans.append(plan1)

    else:
      print 'No solution found.'
  else:
    print 'Specify an instance greater than 0.'

  return plans

def create_data_array():

    import csv
    locations = []
    locations.append([12.999371, 77.668449])

    demands=  []
    demands.append(float(0))
    parent_order = [" "]
    order_list = [" "]
    route_grof =[" "]
    start_times = []
    locations1 = []
    address = []
    new_address = []
    address.append("FCI Godown Rd Dooravani Nagar Bengaluru, Karnataka 560016")
    new_address.append("FCI Godown Rd Dooravani Nagar Bengaluru, Karnataka 560016")
    volume = []
    volume.append(float(0))

    with open('gale/test_new3 - test_new3.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            try:
                row['Length'] = 1
                row['Height'] = 1
                row['Widhth'] = 1
                row['Weight'] = 5
                volume_ind = float(row['Length'])*float(row['Height'])*float(row['Height'])
                ind = row['location'].index(",")

                check = row['Address']
                if check in address:
                    ind = address.index(check)

                    demands[ind] = demands[ind] + float(row['Weight'])
                    volume[ind] = volume[ind] + volume_ind


                else:
                    parent_order.append(row['parent_order'])
                    order_list.append(row['order_list'])
                    route_grof.append(row['Route'])

                    start_times.append(sum(x * int(t) for x, t in zip([3600, 60, 1], row['time'].split(":"))))


                    locations.append([float(row['location'][1:ind]),float(row['location'][ind+1:-1])])
                    demands.append(float(row['Weight']))
                    address.append(row['Address'])
                    new_address.append(row['new_address'])
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



#     start_times =  [3600] * len(locations)

    # tw_duration is the width of the time windows.
    tw_duration = 18000


    # In this example, the width is the same at each location, so we define the end times to be
    # start times + tw_duration. For problems in which the time window widths vary by location,
    # you can explicitly define the list of end_times, as we have done for start_times.
    end_times = [0] * len(start_times)

    for i in range(len(start_times)):
      end_times[i] = start_times[i] + tw_duration
    start_times = [21600] + start_times
    end_times = [50400] + end_times

    data = [locations, demands, start_times, end_times,volume,address,parent_order,order_list,route_grof,new_address]

    return data
if __name__ == '__main__':
  main()
