# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 23:09:25 2019

@author: jakob
"""


from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import pandas as pd
import numpy as np


def get_sd(scrape_dict, key):
    if "elements" in scrape_dict:
        scrape_dict = scrape_dict["elements"]
    if key in scrape_dict:
        return scrape_dict[key]
    for _key, _item in scrape_dict.items():
        if _item["type"] == "tree":
            item = get_sd(scrape_dict[_key], key)
            if item != None:
                return item
    return None


def get_soup(scrape_dict=None, url=None):
    if url==None:
        if scrape_dict==None:
            raise IOError("no scrape_dict and no url!")
        if "url" not in scrape_dict:
            raise IOError("url missing in scrape_dict!")
        url = scrape_dict["url"]
    return BeautifulSoup(urlopen(url).read())


def scrape_content(ed, soup):
    if ed["iterable"] == "true":
        esoup = soup.findAll(ed["tag"],class_=ed["class"])
    else:
        esoup = soup.find(ed["tag"],class_=ed["class"])
    
    # create operations dict for this
    if ed["type"] == "text":
        return esoup.text.strip()
    if ed["type"] == "attribute":
        return esoup[ed["attribute"]]


def scrape_iterable(scrape_dict, soup=None, key=None, ekeys=[]):
            
    if soup == None:
        soup = get_soup(scrape_dict)
    
    sd = None
    if key != None:
        sd = get_sd(scrape_dict, key)
    if sd == None:
        sd = scrape_dict
    
    elements = soup.findAll(sd["tag"],class_=sd["class"])
    edf = pd.DataFrame()
    
    if len(ekeys)==0:
        ekeys = sd["elements"].keys()
    for element_soup in elements:
        row = {}
        for name in ekeys:
            ed = get_sd(sd, name)
            row[name] = scrape_content(ed, element_soup)
        edf = edf.append(row,ignore_index=True)
    return edf


def scrape_listings(cols=[]):
    listing_sd = json.load(open("listing.json"))
    listings = pd.DataFrame()
    i = 1
    while True:
        print(i)
        url = listing_sd["url"] + listing_sd["iter_format"] % i
        i = i+1
        
        listing_soup = get_soup(url=url)
        listing = scrape_iterable(listing_sd, listing_soup, "product", cols)
        if listing.empty:
            break
        listings = listings.append(listing, ignore_index=True)
    return listings


def inquire(column, conditions):
    sel = np.zeros(column.size, bool)
    if len(conditions) == 0:
        return ~sel
    for cond in conditions:
        sel |= np.array([cond.lower() in e.lower() for e in column])
    return sel

def get_custom_listings(listings, brands=[], cpus=[], gpus=[], price_max=None):
    sel = inquire(listings.title, brands)
    sel &= inquire(listings.description, cpus)
    sel &= inquire(listings.description, gpus)
    prices = []
    for pr in listings.price_regular:
        pr = pr.replace(" €","").replace(".","").replace(",",".")
        prices.append(float(pr))
    sel &= np.array(prices) < price_max
    listings["price"] = prices
    return listings[sel]


brands = [
        "Lenovo"
]
cpus = [
        
]
gpus = [
       
]
price_max = 850


listings = scrape_listings()
custom = get_custom_listings(listings,brands,cpus,gpus,price_max)