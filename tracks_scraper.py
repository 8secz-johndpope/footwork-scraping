#! /usr/bin/env python
from __future__ import unicode_literals

import argparse
import demjson
import os
import re
import requests
import soundcloud
import sys
import urllib
import pandas as pd
import pprint
pp = pprint.PrettyPrinter(indent=4)

#from clint.textui import colored, puts, progress
from datetime import datetime
#from mutagen.mp3 import MP3, EasyMP3
#from mutagen.id3 import APIC, WXXX
#from mutagen.id3 import ID3 as OldID3
from subprocess import Popen, PIPE
from os.path import dirname, exists, join
from os import access, mkdir, W_OK

####################################################################

# Please be nice with this!
CLIENT_ID = '175c043157ffae2c6d5fed16c3d95a4c'
CLIENT_SECRET = '99a51990bd81b6a82c901d4cc6828e46'
MAGIC_CLIENT_ID = 'b45b1aa10f1ac2941910a7f0d10f8e28'

AGGRESSIVE_CLIENT_ID = 'OmTFHKYSMLFqnu2HHucmclAptedxWXkq'
APP_VERSION = '1481046241'

####################################################################


# In[2]:


def get_client():
    """
    Return a new SoundCloud Client object.
    """
    client = soundcloud.Client(client_id=CLIENT_ID)
    return client


# In[3]:


# get client
client = get_client()


# In[38]:


# find all sounds of footwork'
page_size = 200
response = client.get('/tracks', q='footwork', limit=page_size,
                    linked_partitioning=1)
#for tracks in tracks.collection:
#    print(track.title)


# In[39]:


response_dict = response.fields()
next_href = response_dict['next_href']
results = response_dict['collection']
result_keys = results[0].keys()
data = pd.DataFrame(results)
data = data.drop(columns=['description'])


# In[40]:


data['title'][len(data)-1]


# In[41]:


data.to_csv('footwork_tracks.csv')


# In[42]:


response_dict = requests.get(next_href).json()
next_href = response_dict['next_href']
results = response_dict['collection']
result_keys = results[0].keys()
new_data = pd.DataFrame(results)
new_data = new_data.drop(columns=['description'])


# In[43]:


new_data


# In[44]:


new_data['title'][0]


# In[45]:


new_data.to_csv('footwork_tracks.csv', mode='a', header=False)

