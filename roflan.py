from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import parse_qs, urlparse
import time


def get_parsed_playlist_without_api(playlist_id, show=True):
    driver = webdriver.Firefox()
    driver.get(f'https://www.youtube.com/playlist?list={playlist_id}')
    driver.implicitly_wait(10)

    three_dots = driver.find_element(By.CSS_SELECTOR, 
            'yt-icon-button[id="button"][class="dropdown-trigger style-scope ytd-menu-renderer"][style-target="button"]')
    three_dots.click()
    show_unavailable_videos = driver.find_element(By.CSS_SELECTOR, 
            'ytd-menu-navigation-item-renderer[class="style-scope ytd-menu-popup-renderer iron-selected"][system-icons=""][role="menuitem"][tabindex="-1"][aria-selected="true"]')
    show_unavailable_videos.click()
    
    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight)')
        time.sleep(2)
        new_height = driver.execute_script('return document.documentElement.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height

    dick = dict(
            playlist_id=playlist_id,
            date=time.ctime(),
            items=dict()
            )
    videos = driver.find_elements(By.TAG_NAME, 'ytd-playlist-video-renderer')
    k = len(videos)
    for video in videos:
        index = k - int(video.find_element(By.ID, 'index').text) + 1
        title = video.find_element(By.ID, 'video-title').text
        if show: print(f'{index}. {title}')
        video_id = parse_qs(urlparse(video.find_element(By.ID, 'video-title').get_attribute('href')).query)['v'][0]
        dick['items'][video_id] = dict(id=index, title=title)
    return dick

