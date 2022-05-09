from googleapiclient.discovery import build
from config import API_KEY
from urllib.parse import urlparse, parse_qs
import json
import os
import time
import sys

#нужно show_difference_between_k_and_m_backups и вообще поменять эту функцию
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


def show_difference_between_backups(curr, prev):
    print('Playlist: ' + curr['playlist_id'])
    print('Current  backup: ' + curr['date'])
    print('Previous backup: ' + prev['date'] + '\n')
    for video_id in curr['items']:
        if video_id in prev['items']:
            if curr['items'][video_id]['title'] != prev['items'][video_id]['title']:
                print(f"--- {curr['items'][video_id]['id']}/{video_id}: {curr['items'][video_id]['title']} <> {prev['items'][video_id]['title']}")
        else:
            print(f"+++ {curr['items'][video_id]['id']}/{video_id}: {curr['items'][video_id]['title']}")
    print('<->')


def show_unavailable_videos(curr):
    reasons = ['Deleted video', 'Private video']
    for video_id in curr['items']:
        if curr['items'][video_id]['title'] in reasons:
            print('{:04}: {} https://www.youtube.com/watch?v={}'.format(*curr['items'][video_id].values(), video_id))
    print('<->')


def playlist_url_handler(url):
    d = urlparse(url).query
    if d:
        return parse_qs(d)['list'][0]
    return url


def main():
    playlist = input('Enter playlist id or url: ')
    PLAYLIST_ID = playlist_url_handler(playlist)
    #PLAYLIST_ID = "PLQE335N_hu3LfshfBTeBpk16Lm6Pj-fjT"

    backup_yes_no = input('Make new backup: [y/n] ')
    try:
        k = max([int(file.split('_')[-1][:4]) for file in os.listdir() if file.startswith(f'playlist_{PLAYLIST_ID}_')])
    except:
        k = 0
    if backup_yes_no[0] == 'y' or backup_yes_no == '1':
        print('Wait...')
        k += 1
        curr_file = open(f'playlist_{PLAYLIST_ID}_{k:04}.json', 'w')
        json.dump(parsed_playlist(PLAYLIST_ID, 0), curr_file, indent=4)
        curr_file.close()
    
    choice = input('Enter number: \n1. Show differences between current playlist backup and previous\n2. Show unavailable videos now \nor [Enter] for exit\n>>> ''')
    while choice:
        if not choice.isdigit():
            break
        match int(choice):
            case 1:   
                try:
                    curr = json.load(open(f'playlist_{PLAYLIST_ID}_{k:04}.json'))
                    prev = json.load(open(f'playlist_{PLAYLIST_ID}_{k-1:04}.json'))
                except:
                    print('Need for Backup')
                    break
                show_difference_between_backups(curr, prev)
            case 2:
                try:
                    curr = json.load(open(f'playlist_{PLAYLIST_ID}_{k:04}.json'))
                except:
                    print('Need for Backup')
                    break
                show_unavailable_videos(curr)

        choice = input('Enter number: \n1. Show differences between current playlist backup and previous\n2. Show unavailable videos now \nor [Enter] for exit\n>>> ''')
if __name__ == '__main__':
    main()
