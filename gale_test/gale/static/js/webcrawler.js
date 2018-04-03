var app = angular.module('webcrawler', []);
app.controller('webcrawlerController', function($scope, $http) {

        
        $scope.tocrawl = function(url,depth){
        var data = {url:url,depth:depth};
        var back_url  = '/web_crawler/';
 
        $http.get(back_url,
            {
            params: data,
          data: JSON
      }).success(function(data, status, headers, config) {
            $scope.final_data = data;
        }
        )
        
        .error(function(data, status, headers, config) {
          
          window.alert("Wrong URL");
          
        });
    
        
};});