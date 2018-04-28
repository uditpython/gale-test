var app = angular.module('webcrawler', ['ngMap']);
app.controller('webcrawlerController', function($scope, $http) {
  //  javascript angular
        $scope.carname = "TATA ACE";
        $scope.center_codinates = "[12.844123, 77.682088]";
   
    var colorsDynamic=['ff8a80','880e4f','4a148c','311b92','3d5afe','76ff03','f57c00','5d4037','0000ff','008080']
  
    
    $scope.vm= {};
    
        var back_url = '/route/';
        $http.get(back_url,
            {
        data: JSON
      }).success(function(data, status, headers, config) {
            var info = {};
            info['depot'] = [];
            var icon = "";
            icon = "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png";
            info['depot'].push([$scope.center_codinates,icon]);
            
            
            var j = -1;
            for (var prop in data){
                j = j+1;
                icon = 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|'+colorsDynamic[j];
                info[prop] = [];
                for (var i = 0; i <data[prop].length; i++) {
                    info[prop].push([data[prop][i],icon]);
                   
                
            }
            
        }
        $scope.final_data = info;
        
        }
        )
        
        .error(function(data, status, headers, config) {
          
          window.alert("Wrong URL");
          return;
        });
    
   
//     $scope.vm.positions =[
//       {pos:[40.71, -74.21]},
//       {pos:[40.72, -74.20]},
//       {pos:[40.73, -74.19]},
//       {pos:[40.74, -74.18]},
//       {pos:[40.75, -74.17]},
//       {pos:[40.76, -74.16]},
//       {pos:[40.77, -74.15]}
//     ];
//    $scope.vm.icons = [];
//    for (var i = 0; i < $scope.vm.positions.length; i++) {
//    
//             $scope.vm.icons.push('http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|'+colorsDynamic[i]);
//             
//             }
           
        
        
        
        
        
        
        
        
        
        
        $scope.tocrawl = function(url,depth){
        
        if (url === ''){
             window.alert("Empty URL");
             return;
        }
        
        if (typeof(url) === 'undefined'){
             window.alert("Empty URL");
             return;
        }
        
        if (typeof(depth) === 'undefined'){
             window.alert("Empty depth");
             return;
        }
        if ( depth === null){
             window.alert("Empty Depth");
             return;
        }
        
        if (!/^(f|ht)tps?:\/\//i.test(url)) {
            url = "http://" + url;
            }
              
              
          // forming the url    
        var data = {url:url,depth:depth};
        var back_url  = '/web_crawler/';
 
        $http.get(back_url,
            {
            params: data,
          data: JSON
      }).success(function(data, status, headers, config) {
            $scope.final_data = data;
            return;
        }
        )
        
        .error(function(data, status, headers, config) {
          
          window.alert("Wrong URL");
          return;
        });
    
        
};});