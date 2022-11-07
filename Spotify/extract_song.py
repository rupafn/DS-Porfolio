"""
    Author: Fajilatun
    This file contains code to extract featured playlist from Spotify
    Then extract the audio features and popularity of the playlist tracks based on their ids
    The featured playlist here I extracted is based in the US
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio
import pandas as pd
import config

# get api credentials (client id and client secret) from https://developer.spotify.com/
# I saved my Spotify api credentials in a config.py file which you will need to create yourself
cid =  config.cid
secret =  config.secret

cm = SpotifyClientCredentials(client_id = cid, client_secret = secret)

sp = spotipy.Spotify(client_credentials_manager = cm)


# get top 50 featured playlist from US
async def get_featured():
    featured = sp.featured_playlists(limit = 50, country='US')
    return featured

# get playlist id from featured playlist 
async def get_playlist_ids(featured):
    playlist_ids = []
    for item in featured['playlists']['items']:
        playlist_ids.append(item['id'])
    print(len(playlist_ids))
    return playlist_ids

def get_popularity(track_id):
    return sp.track(track_id)['popularity']

# get tracks from ids
async def get_track(playlist_ids):
    track_ids = []
    for id in playlist_ids:
        tracks = sp.playlist_tracks(id)
        for item in tracks['items']:
            # print(item['track']['id'])
            try:
                popularity = get_popularity(item['track']['id'])
                track_ids.append({
                    'id': item['track']['id'],
                    'popularity': popularity
                })
                
            except:
                print('No tracks available error')
    return track_ids


async def get_audio_features(tracks):
    length = len(tracks)
    start = 0
    end = 100
    df = pd.DataFrame()
    while end<length:
        track_list = tracks[start:end]
        track_list = pd.DataFrame(track_list)
        features = sp.audio_features(tracks= list(track_list['id']))
        features = pd.DataFrame(features)
        features['popularity'] = track_list['popularity']
        features['id'] = track_list['id']
        if start == 0:
            df = features 
        else: 
            df = pd.concat([df, features])
        start = start+100
        end = end+100
    return df
       
        

if __name__ == '__main__':
    featured = asyncio.run(get_featured())
    playlist_ids = asyncio.run(get_playlist_ids(featured))
    track_ids = asyncio.run(get_track(playlist_ids))
    df = asyncio.run(get_audio_features(track_ids))
    df.to_csv('out.csv', index=False)

