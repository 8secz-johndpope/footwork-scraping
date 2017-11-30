#! /usr/bin/env python

import os
import requests
import soundcloud
import pandas as pd
from datetime import datetime
from time import sleep
import logging
import pickle

####################################################################

# Please be nice with this!
CLIENT_ID = '175c043157ffae2c6d5fed16c3d95a4c'
CLIENT_SECRET = '99a51990bd81b6a82c901d4cc6828e46'
MAGIC_CLIENT_ID = 'b45b1aa10f1ac2941910a7f0d10f8e28'

AGGRESSIVE_CLIENT_ID = 'OmTFHKYSMLFqnu2HHucmclAptedxWXkq'
APP_VERSION = '1481046241'

# page size of 200 seems to work nicely, even though the API
# seems to return 180-200 results per request
PAGE_SIZE = 200
# Sleep time between requests - 4 seconds so as to not overload the server
SLEEP_TIME = 4

####################################################################

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='./footwork_tracks.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

####################################################################

def get_client():
    """
    Return a new SoundCloud Client object.
    """
    client = soundcloud.Client(client_id=CLIENT_ID)
    return client

### Main Script ###
client = get_client()

try:
	# find all tracks with footwork tag
	response = client.get('/tracks', q='footwork', limit=PAGE_SIZE,
	                    linked_partitioning=1)
	counter = 1
	# parse dictionary of response
	response_dict = response.fields()
	next_href = False
	if('next_href' in response_dict):
		next_href = response_dict['next_href']
	if('collection' in response_dict):
		results = response_dict['collection']
		result_keys = results[0].keys()
		data = pd.DataFrame(results)
		data = data.drop(columns=['description'])
		# write initial dataframe to file, overwriting any previous file
		data.to_csv('footwork_tracks.csv')
		logging.info('Got ' + str(len(data)) + ' results from first request ')
	while (next_href):
		counter = counter + 1
		logging.info('Next request to: ' + next_href)
		response = requests.get(next_href)
		pickle.dump( response, open( "last_API_response.p", "wb" ) )
		response_dict = response.json()
		if('next_href' in response_dict):
			next_href = response_dict['next_href']
		else:
			next_href = False
		if('collection' in response_dict):
			results = response_dict['collection']
			result_keys = results[0].keys()
			data = pd.DataFrame(results)
			data = data.drop(columns=['description'])
			# append next set of results to file
			data.to_csv('footwork_tracks.csv', mode='a', header=False)
			logging.info('Got ' + str(len(data)) + ' results from request ' + str(counter))
		else:
			# Now, we can log to the root logger, or any other logger. First the root...
			logging.info('No collection of results returned')
			#print("No collection of results returned")
		logging.info('Sleeping ' + str(SLEEP_TIME) + ' seconds at ' + str(datetime.now()))
		#print('Sleeping ' + SLEEP_TIME + ' seconds at ' + str(datetime.now()))
		sleep(SLEEP_TIME)
	logging.info('All tracks pulled. Finishing at ' + str(datetime.now()))

except Exception as e:
	logging.info('Error from API request: ' + str(e))

