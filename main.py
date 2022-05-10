from googleapiclient.discovery import build
from config import API_KEY
from urllib.parse import urlparse, parse_qs
import json
import os
import time
import sys


def get_parsed_playlist(playlist_id="PLQE335N_hu3LfshfBTeBpk16Lm6Pj-fjT", show=False):
    main_dict = dict(
            playlist_id=playlist_id,
            date=time.ctime(),
            items=dict()
            )
    token = None
    to_exit = ''
    while True:
        try:
            request = build("youtube", "v3", developerKey=API_KEY).playlistItems().list(
                part="snippet",
                maxResults=50,
                pageToken=token,
                playlistId=playlist_id
                )
            response = request.execute()
        except Exception as err:
            to_exit = str(err)
            break
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
    if to_exit: sys.exit('Something went wrong: ' + to_exit)
    return main_dict


def show_difference_between_backups(m, n):
    print('<->')
    print('Playlist: ' + m['playlist_id'])
    print('Newer backup: ' + m['date'])
    print('Older backup: ' + n['date'] + '\n')
    
    diff_pros = set(m['items']) - set(n['items'])
    diff_cons = set(n['items']) - set(m['items'])
    no_diff = set(m['items']) & set(n['items'])
    for video_id in sorted(diff_pros, key=lambda x: m['items'][x]['id']):
        print(f"+++ {m['items'][video_id]['id']}|https://www.youtube.com/watch?v={video_id}: {m['items'][video_id]['title']}")
    
    for video_id in sorted(diff_cons, key=lambda x: n['items'][x]['id']):
        print(f"--- {n['items'][video_id]['id']}|https://www.youtube.com/watch?v={video_id}: {n['items'][video_id]['title']}")
    
    for video_id in sorted(no_diff, key=lambda x: m['items'][x]['id']):
        if video_id in n['items']:
            if m['items'][video_id]['title'] != n['items'][video_id]['title']:
                print(f"*** {m['items'][video_id]['id']}|https://www.youtube.com/watch?v={video_id}: {m['items'][video_id]['title']} <> {n['items'][video_id]['title']}")
    print('<->')


def show_unavailable_videos(curr):
    print('<->')
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


def existing_playlists_in_path(path='.'):
    return sorted(set([x[9:-10] for x in os.listdir(path) if x.startswith('playlist_') and x.endswith('.json')]))


def main():
    fapah = existing_playlists_in_path('.')
    if fapah:
        print('Playlists, which have backups: ')
        _k = 0
        for pl in fapah:
            _k += 1
            print(f'#{_k}. {pl}')
        playlist = input('Enter playlist id or url or num (e.g. #1): ')
        if playlist[0] == '#':
            PLAYLIST_ID = fapah[(int(playlist[1:])-1)%len(fapah)]
        else:
            PLAYLIST_ID = playlist_url_handler(playlist)
    else:
        playlist = input('Enter playlist id or url: ')
        PLAYLIST_ID = playlist_url_handler(playlist)

    backup_yes_no = input('Make new backup: [y/n] ')
    try:
        k = max([int(file.split('_')[-1][:4]) for file in os.listdir() if file.startswith(f'playlist_{PLAYLIST_ID}_')])
    except:
        k = 0
    if backup_yes_no and (backup_yes_no[0] == 'y' or backup_yes_no == '1'):
        print('Wait...')
        k += 1
        parsed_playlist = get_parsed_playlist(PLAYLIST_ID,0)
        curr_file = open(f'playlist_{PLAYLIST_ID}_{k:04}.json', 'w')
        json.dump(parsed_playlist, curr_file, indent=4)
        curr_file.close()
    str_for_input = 'Enter number: \n1. Show differences between current playlist backup and previous\n2. Show unavailable videos now\n3. Show differences between m and n backups (m>n)\nor [Enter] for exit\n>>> '
    choice = input(str_for_input)
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
            case 3:
                playlist_nums = sorted([int(file.split('_')[-1][:4]) for file in os.listdir() if file.startswith(f'playlist_{PLAYLIST_ID}_')])
                if playlist_nums:
                    try:
                        m = int(input(f'Choose m => {playlist_nums}: '))%(k+1)
                        n = int(input(f'Choose n => {playlist_nums}: '))%(k+1)
                    except ValueError:
                        print('m, n are int')
                        break
                    if n>m: m,n = n,m
                else:
                    print('Need for Backup')
                    break
                f_m = json.load(open(f'playlist_{PLAYLIST_ID}_{m:04}.json'))
                f_n = json.load(open(f'playlist_{PLAYLIST_ID}_{n:04}.json'))
                show_difference_between_backups(f_m, f_n)

        choice = input(str_for_input)


if __name__ == '__main__':
    main()
