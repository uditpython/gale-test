from django.conf.urls import url
from gale import views

urlpatterns = [
              url(r'^$',views.home),
              url(r'^web_crawler/$', views.web_crawler, ),
              url(r'^route/$', views.route, ),
              
              
                       
                       
             ]