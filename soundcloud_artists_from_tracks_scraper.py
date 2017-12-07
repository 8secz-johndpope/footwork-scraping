
# coding: utf-8

# In[37]:


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

# Please be nice with this!
CLIENT_ID = '175c043157ffae2c6d5fed16c3d95a4c'
CLIENT_SECRET = '99a51990bd81b6a82c901d4cc6828e46'
MAGIC_CLIENT_ID = 'b45b1aa10f1ac2941910a7f0d10f8e28'

AGGRESSIVE_CLIENT_ID = 'OmTFHKYSMLFqnu2HHucmclAptedxWXkq'
APP_VERSION = '1481046241'

####################################################################

# Sleep time between requests - 2 seconds so as to not overload the server
SLEEP_TIME = 2
inFileName = './data/soundcloud_footwork_tracks_tag.csv'
outFileName = './data/soundcloud_footwork_artists_from_tracks.csv'

####################################################################


# In[5]:


def get_client():
    """
    Return a new SoundCloud Client object.
    """
    client = soundcloud.Client(client_id=CLIENT_ID)
    return client


# In[6]:


# get client
client = get_client()


# In[5]:


# find all sounds of footwork'
response = client.get('/users', q='footwork', limit=page_size,
                    linked_partitioning=1)
#for tracks in tracks.collection:
#    print(track.title)


# In[12]:


response_dict = response.fields()
next_href = response_dict['next_href']
results = response_dict['collection']
result_keys = results[0].keys()
data = pd.DataFrame(results)
data = data.drop(columns=['description'])


# In[40]:


data['title'][len(data)-1]


# In[13]:


data.to_csv('footwork_artists.csv')


# In[42]:


response_dict = requests.get(next_href).json()
next_href = response_dict['next_href']
results = response_dict['collection']
result_keys = results[0].keys()
new_data = pd.DataFrame(results)
new_data = new_data.drop(columns=['description'])


# In[45]:


new_data.to_csv('footwork_tracks.csv', mode='a', header=False)


# In[7]:


# Generate list of artists to query from list
# of tracks tagged with footwork
tracks = pd.read_csv(inFileName)


# In[14]:


tracks.columns


# In[97]:


tracks['download_count'][0]


# In[47]:


response = client.get('/users/1918080')


# In[48]:


user = response.fields()


# In[49]:


user['description'] = user['description'].replace('\n', ' ').encode("ascii", errors="ignore").decode().strip()


# In[50]:


with open(outFileName, 'w') as outFile:  # Just use 'w' mode in 3.x
    outFileWriter = csv.DictWriter(outFile, user.keys())
    outFileWriter.writeheader()
    outFileWriter.writerow(user)


# In[ ]:


# Group by artist to get aggregate stats so we can sort and query in a sensible order
# sum is the total number of downlaods per artist across all tracks in list
# count is the total number of tracks in the list per artist
grouped = tracks[['user_id', 'download_count']].groupby('user_id')
aggregated = grouped.agg(['sum', 'count'])
# remove the multiindex
aggregated.columns = aggregated.columns.droplevel()
sorted_artists = aggregated.sort_values(by='sum', ascending=False)
sorted_user_id_list = list(sorted_artists.index)


# In[104]:




