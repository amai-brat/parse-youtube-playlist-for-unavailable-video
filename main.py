from googleapiclient.discovery import build
from config import API_KEY
import json
import os
import time
import sys


def parsed_playlist(playlist_id="PLQE335N_hu3LfshfBTeBpk16Lm6Pj-fjT", show=False):
    main_dict = dict(
            playlist_id=playlist_id,
            date=time.ctime(),
            items=dict()
            )
    token = None
    while True:
        request = build("youtube", "v3", developerKey=API_KEY).playlistItems().list(
            part="snippet",
            maxResults=50,
            pageToken=token,
            playlistId=playlist_id
            )
        response = request.execute()
        num = response["pageInfo"]["totalResults"]
        for video in response["items"]:
            if show:
                print(video['snippet']['title'])
            if video["snippet"]["thumbnails"]:
                main_dict["items"][video['snippet']['resourceId']['videoId']] = dict(
                        id=num - video["snippet"]["position"],
                        title=video["snippet"]["title"]) 
            else:
                main_dict["items"][video['snippet']['resourceId']['videoId']] = dict(
                        id=num - video["snippet"]["position"],
                        title=video["snippet"]["title"])

        if response.get("nextPageToken"):
            token = response["nextPageToken"]
        else:
            break
    return main_dict


def show_difference_between_playlists(curr, prev):
    print('Playlist: ' + curr['playlist_id'])
    print('Current playlist: ' + curr['date'])
    print('Previous playlist: ' + prev['date'])
    for video_id in curr['items']:
        if video_id in prev['items']:
            if curr['items'][video_id]['title'] != prev['items'][video_id]['title']:
                print(f"--- {curr['items'][video_id]['id']}/{video_id}: {curr['items'][video_id]['title']} <> {prev['items'][video_id]['title']}")
        else:
            print(f"+++ {curr['items'][video_id]['id']}/{video_id}: {curr['items'][video_id]['title']}")


def show_unavailable_videos(curr):
    reasons = ['Deleted video', 'Private video']
    for video_id in curr['items']:
        if curr['items'][video_id]['title'] in reasons:
            print('{:04}: {} {}'.format(*curr['items'][video_id].values(), video_id))

def main():
    PLAYLIST_ID = "PLQE335N_hu3LfshfBTeBpk16Lm6Pj-fjT" 
    try:
        k = max([int(file.split('_')[-1]) for file in os.listdir() if file.startswith(f'playlist_{PLAYLIST_ID}_')])+1
    except:
        k = 0
    curr_file = open(f'playlist_{PLAYLIST_ID}_{k:04}.json', 'a+')
    json.dump(parsed_playlist(PLAYLIST_ID, 1), curr_file, indent=4)
    curr_file.close()
    show_unavailable_videos(json.load(open(f'playlist_{PLAYLIST_ID}_{k:04}.json')))


if __name__ == '__main__':
    main()
