from django.conf.urls import url
from gale import views

urlpatterns = [
              url(r'^$',views.home),
              url(r'^web_crawler/$', views.web_crawler, ),
              url(r'^route/$', views.route, ),
              url(r'^routedetail/$', views.create_excel, ),
              url(r'^predefined_routes/$', views.noptimize, ),
              url(r'^dist/$', views.distance_matrix, ),
              url(r'^report_info/$', views.ReportInfo, ),
            url(r'^barcode/$', views.barcode, ),
             url(r'^inventory_mongo/$', views.inventory, ),
              url(r'^inventory_data/$', views.inventory_data, ),
               url(r'^price_mongo/$', views.price_mongo, ),
                url(r'^route_mongo/$', views.route_mongo, ),
                url(r'^redeliver/$', views.redeliver, ),
                url(r'^redelivery_points/$', views.redelivery_points, ),
                
              
                       
                       
             ]