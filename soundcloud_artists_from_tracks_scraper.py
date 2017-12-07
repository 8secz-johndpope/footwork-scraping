#! /usr/bin/env python

import os
import requests
import soundcloud
import pandas as pd
from datetime import datetime
from time import sleep
import logging
import csv
from pprint import pprint as pp


####################################################################

# Starting Point - 0 if starting from the beginning, or the index of
# the last user in sorted_user_id_list if we were interrupted
STARTING_INDEX = 550

# Sleep time between requests - 4 seconds so as to not overload the server
SLEEP_TIME = 4
inFileName = './data/soundcloud_footwork_tracks_tag.csv'
outFileName = './data/soundcloud_footwork_artists_from_tracks_v2.csv'

####################################################################

# Please be nice with this!
CLIENT_ID = '175c043157ffae2c6d5fed16c3d95a4c'
CLIENT_SECRET = '99a51990bd81b6a82c901d4cc6828e46'
MAGIC_CLIENT_ID = 'b45b1aa10f1ac2941910a7f0d10f8e28'

AGGRESSIVE_CLIENT_ID = 'OmTFHKYSMLFqnu2HHucmclAptedxWXkq'
APP_VERSION = '1481046241'

####################################################################

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='./logs/footwork_artists_from_tracks.log',
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

def get_user_dict_from_client(client, user_id):
    query = '/users/' + str(user_id)
    response = client.get(query)
    user = response.fields()
    try:
### Tried to strip user descriptions down to simple characters but it still broke
### Maybe on commas?
#        user['description'] = user['description'].replace('\n', ' ') \
#                .encode("ascii", errors="ignore").decode().strip()
        # remove the description field in place, b/c it is causing csv issues
        user.pop('description', 0)
    except:
        logging.info('user had no description')
    return user

def get_artists_and_append_to_csv(user_id_list, outFileWriter, starting_idx):
    # Interate through the entire list of artists
    for i, user_id in enumerate(user_id_list[starting_idx:]):
        idx = i + starting_idx
        logging.info('Sending request # ' + str(idx) + ' for user_id: ' 
                + str(user_id))
        user = get_user_dict_from_client(client, user_id)
        outFileWriter.writerow(user)
        logging.info('Successfully recorded user in csv; ' + 
            'Sleeping ' + str(SLEEP_TIME) + ' seconds at ' + str(datetime.now()))
        sleep(SLEEP_TIME)
    logging.info('All artists pulled. Finishing at ' + str(datetime.now()))

### Main Script ###
client = get_client()

# Generate list of artists to query from list
# of tracks tagged with footwork
tracks = pd.read_csv(inFileName)
# Group and agg by artist so that we can sort and query in a sensible order
# sum is the total number of downlaods per artist across all tracks in list
# count is the total number of tracks in the list per artist
grouped = tracks[['user_id', 'download_count']].groupby('user_id')
aggregated = grouped.agg(['sum', 'count'])
# remove the multiindex
aggregated.columns = aggregated.columns.droplevel()
sorted_artist_data = aggregated.sort_values(by='sum', ascending=False)
sorted_user_id_list = list(sorted_artist_data.index)

if (0 == STARTING_INDEX):
    with open(outFileName, 'w') as outFile:
        try:
            # run the first query and set up the csv file with a header row
            user = get_user_dict_from_client(client, sorted_user_id_list[0])
            outFileWriter = csv.DictWriter(outFile, sorted(user.keys()))
            outFileWriter.writeheader()
            outFileWriter.writerow(user)
            logging.info('First Entry: user_id: ' + str(user['id']))
            get_artists_and_append_to_csv(sorted_user_id_list, outFileWriter, 1)
            # # Interate through the entire list of artists
            # for i, user_id in enumerate(sorted_user_id_list):
            #     logging.info('Sending request # ' + str(i) + ' for user_id: ' 
            #             + str(user_id))
            #     user = get_user_dict_from_client(client, user_id)
            #     outFileWriter.writerow(user)
            #     logging.info('Successfully recorded user in csv; ' + 
            #         'Sleeping ' + str(SLEEP_TIME) + ' seconds at ' + str(datetime.now()))
            #     sleep(SLEEP_TIME)
            # logging.info('All artists pulled. Finishing at ' + str(datetime.now()))
        except Exception as e:
            logging.info('Error from API request: ' + str(e))
else:
    with open(outFileName, 'a') as outFile:
        try:
            user = get_user_dict_from_client(client, sorted_user_id_list[0])
            outFileWriter = csv.DictWriter(outFile, sorted(user.keys()))
            get_artists_and_append_to_csv(sorted_user_id_list, outFileWriter, STARTING_INDEX)
        except Exception as e:
            logging.info('Error from API request: ' + str(e))
