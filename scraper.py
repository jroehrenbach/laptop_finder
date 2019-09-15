# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 23:09:25 2019

@author: jakob
"""


from urllib.request import urlopen
from bs4 import BeautifulSoup
import json



def get_dict(scrape_dict, key):
    if key in scrape_dict:
        return scrape_dict[key]
    for _key, _item in scrape_dict.items():
        if _item["type"] == "tree":
            item = get_dict(scrape_dict[_key], key)
            if item != None:
                return item
    return None

def get_soup(scrape_dict, url=None):
    if url==None:
        if "url" not in scrape_dict:
            raise IOError("url missing in scrape_dict!")
        url = scrape_dict["url"]
    return BeautifulSoup(urlopen(url).read())

def scrape_iterable(scrape_dict, soup=None, key=None, ekeys=[]):
            
    if soup == None:
        soup = get_soup(scrape_dict)
    
    if key != None:
        sd = get_dict(scrape_dict, key)
        if sd == None: sd = scrape_dict
    
    elements = soup.findAll(sd["tag"],class_=sd["class"])
    return elements



listing_sd = json.load(open("listing.json"))
listing_soup = get_soup(listing_sd)

elements = scrape_iterable(listing_sd, listing_soup, "product")