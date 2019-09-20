# laptop_finder
Enter desired details and scrape entire website
If match was found an email will be sent to a target address
<br /><br />

### Requirements
Python 3.6
<br />
bs4
<br />
json
<br />
pandas
<br />
numpy
<br />
smtplib
<br /><br />

### How to run it
Change following parameters in "main" - function in scraper.py:
<br />
origin_addr, target_addr, origin_pwd
<br /><br />

### scraper.py
Script for scraping desired website and sending matches to target email address.
<br /><br />

### listings.json
json script which contains scrape_dicts for desired objects on listing page
<br /><br />

### product.json
json script which contains scrape_dicts for further details of single product.
<br />
Note: This feature is still in process
<br /><br />

### scrape_dict
dict which is used for scraping desired data
#### Members:
tag
<br />
class
<br />
type
<br />
iterable
<br />
elements (optional)
<br /><br />

### conditions
...
<br /><br /><br />

## TO DO:
- scrape using product.json
