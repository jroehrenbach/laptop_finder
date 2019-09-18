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
import smtplib



def get_sd(scrape_dict, key):
    """
    Extracts sub-scrape_dict at key if it exists in scrape_dict
    
    Parameters
    ----------
    scrape_dict : dict
        dict which contains instructions for scraping certain object.
        Further information in README.md
    key : str
        key to desired scrape_dict
    
    Returns
    -------
    sub_sd : dict
        scrape_dict at key if found, otherwise None
    """
    
    if "elements" in scrape_dict:
        scrape_dict = scrape_dict["elements"]
    if key in scrape_dict:
        return scrape_dict[key]
    for _key, _item in scrape_dict.items():
        if _item["type"] == "tree":
            sub_sd = get_sd(scrape_dict[_key], key)
            if sub_sd != None:
                return sub_sd
    return None


def get_soup(scrape_dict=None, url=None):
    """
    Returns BeautifulSoup object if page available
    
    Parameters
    ----------
    scrape_dict : dict (optional)
        dict which contains instructions for scraping certain object.
        Further information in README.md
    url : str
        url of desired page
    
    Returns
    -------
    BeautifulSoup of desired page
    """
    
    if url==None:
        if scrape_dict==None:
            raise IOError("no scrape_dict and no url!")
        if "url" not in scrape_dict:
            raise IOError("url missing in scrape_dict!")
        url = scrape_dict["url"]
    return BeautifulSoup(urlopen(url).read())


def scrape_content(ed, soup):
    """
    Scrapes desired object from BeautifulSoup using scrape_dict
    
    Parameters
    ----------
    ed : dict
        scrape_dict for desired object
        Further information in README.md
    soup : BeautifulSoup
        BeautifulSoup object from which desired object should be scraped
    
    Returns
    -------
    Desired object
    """
    
    if ed["iterable"] == "true":
        esoup = soup.findAll(ed["tag"],class_=ed["class"])
    else:
        esoup = soup.find(ed["tag"],class_=ed["class"])
    
    # create operations dict for this
    if ed["type"] == "text":
        return esoup.text.strip()
    if ed["type"] == "attribute":
        return esoup[ed["attribute"]]


def scrape_listing_page(scrape_dict, soup=None, key=None, ekeys=[]):
    """
    Scrapes all objects as in scrape_dict
    
    Parameters
    ----------
    scrape_dict : dict
        dict which contains instructions for scraping certain object.
        Further information in README.md
        Note: iterable must be true
    soup : BeautifulSoup (optional)
        BeautifulSoup object from which desired object should be scraped
    key : str (optional)
        Key to sub-scrape_dict
    ekeys : list
        List of keys of desired objects within iterable object
    
    Returns
    -------
    edf : pd.DataFrame
        Data Frame which contains desired data
    """
            
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
    """
    Scrapes all available pages with listings
    
    Parameters
    ----------
    cols : list
        list of keys for desired data
    
    Returns
    -------
    listings : pd.DataFrame
        Data frame which contains desired data
    """
    
    listing_sd = json.load(open("listing.json"))
    listings = pd.DataFrame()
    i = 1
    while True:
        print(i)
        url = listing_sd["url"] + listing_sd["iter_format"] % i
        i = i+1
        
        listing_soup = get_soup(url=url)
        listing = scrape_listing_page(listing_sd, listing_soup, "product", cols)
        if listing.empty:
            break
        listings = listings.append(listing, ignore_index=True)
    return listings


def inquire(column, condition_list):
    """
    Checks which rows match conditions in condition_list
    
    Parameters
    ----------
    column : pd.Series
        Contains data which will be checked
    condition_list : list
        List of str which should be in column
    
    Returns
    -------
    sel : np.array (bool)
        Bool array with same shape as column and which is true where
        condition_list is matched
    """
    
    sel = np.ones(column.size, bool)
    if len(condition_list) == 0:
        return ~sel
    for cond in condition_list:
        if type(cond) == list:
            _sel = np.zeros(column.size, bool)
            for c in cond:
                _sel |= column.str.contains(c)
            sel &= _sel
        else:
            sel &= column.str.contains(cond)
    return sel


def get_numeric(column):
    """
    For turning raw data to numerical
    
    Parameters
    ----------
    column : pd.Series
        Contains data which should be transformed to numerical
    
    Returns
    -------
    transformed data
    
    Note
    ----
    This function is in process. More features will be added.
    """
    
    all_args = [("€",""),("%",""),(".",""),(",",".")]
    for args in all_args:
        column = column.str.replace(*args)
    return column.astype(float)


def get_custom_listings(listings, conditions, price_max=None):
    """
    Function for customizing data
    
    Parameters
    ----------
    listings : pd.DataFrame
        Data frame as returned from scrape_listings
    conditions: dict
        Dict with conditions as described in README.md
    price_max : float
        Maximum price
    
    Returns
    -------
    Custom listings
    """
    
    sel = np.ones(listings.shape[0], bool)
    for col, cond in conditions.items():
        sel &= inquire(listings[col], cond)
    listings["price"] = get_numeric(listings.price_regular)
    sel &= listings.price < price_max
    return listings[sel]


def send_email(message, gmail_addr, target_addr, pwd):
    """
    Sends email with message to to target_addr
    
    Parameters
    ----------
    message : str
    gmail_addr : str
    target_addr : str
    pwd : str
    """
    
    try:
        server = smtplib.SMTP('smtp.gmail.com',587)
        
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        #Next, log in to the server
        server.login(gmail_addr, pwd)
        
        #Send the mail
        msg = "\r\n".join([
          "From: %s" % gmail_addr,
          "To: %s" % target_addr,
          "Subject: laptop_finder",
          "",
          message
          ])
        server.sendmail(gmail_addr, target_addr, msg)
        
        server.quit()
        print("email was sent!")
        
    except:
        print("sending email failed...")


def main():
    conditions = {
            "title": ["Lenovo"],
            "description": [["GTX","GTR"],"i7","15,6"]
    }
    price_max = 850
    
    listings = scrape_listings()
    custom = get_custom_listings(listings,conditions,price_max)
    
    if custom.empty:
        return
    
    urls = "\n".join(custom.url)
    message = "Check out these laptops:\n" + urls
    gmail_addr = "jroehrenbach@gmail.com"
    target_addr = "jroehrenbach@aol.de"
    app_pwd = "vazo zsjk pcqq kbcf"
    send_email(message, gmail_addr, target_addr, app_pwd)


if __file__ == "__main__":
    main()