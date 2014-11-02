# -*- coding: utf-8 -*-
"""
Credit to YoApp/BarRecommender from https://github.com/YoApp/BarRecommendor/

Yo single tap lunch recommendation
Yo Docs: http://docs.justyo.co
Yo Keys: http://dev.justyo.co

Yelp code from https://github.com/Yelp/yelp-api/blob/master/v2/python/sample.py
Yelp Docs: http://www.yelp.com/developers/documentation
Yelp Keys: http://www.yelp.com/developers/manage_api_keys

"""
import random
import sys
import requests
import oauth2
import urllib
import urllib2
import json
from flask import request, Flask


API_HOST = 'api.yelp.com'
SEARCH_LIMIT = 20
SEARCH_OFFSET = 20
SEARCH_PATH = '/v2/search?'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.
# Yelp Keys: http://www.yelp.com/developers/manage_api_keys
CONSUMER_KEY = '7csfR86YeNesyGPjoP-P_Q'
CONSUMER_SECRET = 'OGAPP1o4gsBTR-MoJ-eVFzk5aRU'
TOKEN = 'aZll3F1Fl_IDodqA0iT3ZjviQtzqLV0t'
TOKEN_SECRET = 'dZXozaW2bt3xgwZCV46lcaps3Sw'

# Yo API Token: http://dev.justyo.co
YO_API_TOKEN = 'de1e7a13-2440-468c-b03a-9a90ff3d2d8e'


if len(CONSUMER_KEY) == 0 or \
    len(CONSUMER_SECRET) == 0 or \
    len(TOKEN) == 0 or \
    len(TOKEN_SECRET) == 0 or \
    len(YO_API_TOKEN) == 0:
    print 'fill the tokens for Yelp'
    sys.exit(1)


def do_request(host, path, url_params=None):
    
    url = 'http://{0}{1}?'.format(host, path)

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print 'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, city, latitude, longitude):
    
    url_params = {
        #'category_filter': 'restaurants',
        #'offset': SEARCH_OFFSET,
        'term': term.replace(' ', '+'),
        'location': city.replace(' ', '+'),
        'cll': latitude + ',' + longitude,
        'limit': SEARCH_LIMIT,
        'sort': 2, # highest rated
        'radius_filter': 8000 # five miles
    }

    return do_request(API_HOST, SEARCH_PATH, url_params=url_params)


app = Flask(__name__)


@app.route("/yo/")
def yo():

    # extract and parse query parameters
    username = request.args.get('username')
    location = request.args.get('location')
    splitted = location.split(';')
    latitude = splitted[0]
    longitude = splitted[1]

    print "We got a Yo from " + username

    # get the city name since Yelp api must be provided with at least a city even though we give it accurate coordinates
    response = requests.get('http://nominatim.openstreetmap.org/reverse?format=json&lat=' + latitude + '&lon=' +longitude + '&zoom=18&addressdetails=1')
    response_object = response.json()
    city = response_object['address']['city']

    print username + " is at " + city

    # search for restaurants using Yelp api
    response = search('lunch', city, latitude, longitude)

    print response
    # grab the a random result
    restaurant = response['businesses'][random.randint(0,len(response['businesses']))-1]
    #restaurant = response['businesses'][0]

    restaurant_url = restaurant['mobile_url']

    print "Grab lunch at " + restaurant['name']

    # Yo the result back to the user
    requests.post("http://api.justyo.co/yo/", data={'api_token': YO_API_TOKEN, 'username': username, 'link': restaurant_url})

    # OK!
    return 'OK'

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
