var app = angular.module('webcrawler', []);
app.controller('webcrawlerController', function($scope, $http) {
  //  javascript angular
        
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