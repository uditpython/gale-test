# -*- coding: utf-8 -*-
import threading
from __future__ import unicode_literals
import requests
import time
from django.shortcuts import render
from django.http.response import HttpResponse
import json
from bs4 import BeautifulSoup
from settings import NUMBER_OF_THREADS

# Create your views here.
def home(request):
    template = 'gale/index.html'
    return render(request,template)

def get_data(url,session):
    url_data = session.get(url)
    
    soup = BeautifulSoup(url_data.text,"html.parser")
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
            
            links_to_be_shown.append(final_link)   
    
    tags_shown = []
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
        
    
    links_to_be_shown = list(set(links_to_be_shown))
    tags_shown = list(set(tags_shown))
    data = {}
    data['links'] = links_to_be_shown
    data['images'] = tags_shown

    return data
    
    
    
def validate_images(image_list,session):
        valid_images = []
        for images in image_list:
           response = session.get(images)
           if response.status_code == 200:
               valid_images.append(images)
        return valid_images
    
def validate_urls(url_list,session):
        valid_urls = []
        for i in url_list:
            try:
                s = session.get(i)
                valid_urls.append(i)
            except:
                pass
        return valid_urls
    
    
    




    
        




    
    
    
    
    
    
    
    
    
    
    

def web_crawler(request):
    url = request.GET.get('url',None)
    
    depth = int(request.GET.get('depth',None))
    session = requests.Session()
    
    data = get_data(url,session)
    seed_urls_to_be_expolred = data['links']
    seed_urls_explored = []
    images_list = data['images']
    if depth == 0:
        seed_urls_explored = validate_urls(seed_urls_to_be_expolred)
        
    else:
        depth_initial = 1
        
        
        while depth_initial <= depth:
            create_workers()
            temp_urls = []
            if len(seed_urls_to_be_expolred) > 0:
                create_jobs()
                for (i,j) in enumerate(seed_urls_to_be_expolred):
                    if j not in seed_urls_explored:
                        try:
                            new_data = get_data(j,session)
                            
                            temp_urls  +=  new_data['links']
                            images_list +=  new_data['images']
                            seed_urls_explored.append(j)
                        except Exception as e:
                            pass
                    
             
            seed_urls_to_be_expolred = list(set(temp_urls))
            
            
            depth_initial += 1    
        
        if len(seed_urls_to_be_expolred) > 0:
            seed_urls_explored += validate_urls(seed_urls_to_be_expolred,session)
    
    final_data = {}
    final_data['links'] = seed_urls_explored
    final_data['images'] = validate_images(list(set(images_list)),session)
        
    return HttpResponse(json.dumps(final_data) , content_type="application/json")
    
    