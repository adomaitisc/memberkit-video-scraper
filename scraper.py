import os
import re
import unicodedata
import requests
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup
from vimeo_downloader import Vimeo

# Base URL
BASE_URL = "https://profissao-investidor.memberkit.com.br/"

# Video base URL
VIDEO_BASE_URL = "https://vimeo.com/api/oembed.json?url=https%3A%2F%2Fvimeo.com%2FVIDEO_ID&width=640&id=VIDEO_ID&title=false&byline=false&portrait=false&sidedock=false&speed=true&transparent=false&color=4f46e5"

# Courses URLs
COURSES = [
    '12134-profissao-investidor-commodities',
    '43922-renda-fixa-profissional',
    '61479-operacao-de-ciclo-do-dolar'
]

# Cookie string
RAW_COOKIES = "remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3lOems1T1RjMVhTd2lKREpoSkRFeEpISmlhVGRRWWtWVlVrTlBVSGRPY0ZVeVlqQTJkeTRpTENJeE5qWTRPVGMxTURFMUxqTXdNekU1TWpFaVhRPT0iLCJleHAiOiIyMDIyLTEyLTA0VDIwOjEwOjE1LjMwM1oiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ==--72278cf67210a415825977951136e06142741831; _memberkit_session=IjAaqECNoPiTw5KeMzgG2XFFHk+7V3BAVr2nMRoz9Z4+H0S67O6lmj3YTRgKWSQAIyvAzOUgk0SHEJWbB1u0b+OGAQs1f8LovmoUtBQocpsy7ezwvH7rnRCwlgVGly6mymJpEe1+aHudkoAF3a5zeY/pMOlwCkilIDHSOlgdTe31uPHhC0z2ab/V6sUHSSZwPSfxL64bd5WEKqAk+Czk0sAn/zSCc7Af8Wd+fTSN8ELOm3QrCi8bJUiSHoMVZTUwpbjnTzi80B0Pg5wmkxeao3S8Vz9MabJqpL3FZvpsI9LNPxxWV5GcaJ4gQC0HN+aV4yS5vVCkY1ju/IQbdZ66GGr2BDOpVOcK2z5s9xMGU5OJ+3daLUIhUQG70uhDOr3FHyKOayJd0Kus/MZmZd7cHU0F13EcIE6CahVY3HNISWgeu3mu32XyrF2EfwLyLsiGYefXLWvbiL5PqdxiFLoX00n6fIJexQoguhMW3I3JNpK2K07iXsy0gBnQf6usbKaMzjrIS/xA0VvVnHMelsoLDaTn--UuqVPbUDV8UC7dt1--krdoev1HRT+0IxiSYDil2A=="

# Parsed cookies
COOKIES = SimpleCookie().load(RAW_COOKIES)

# HTTP headers
HEADERS = {
    'Cookie': RAW_COOKIES,
}

# function to validade video id
def validate_video_id(video_id):
    if video_id is None:
        return False
    if len(video_id) != 9:
        return False
    if not video_id.isdigit():
        return False
    return True

# function to get a valid pathname from a string
# taken from django source code
def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def verify_downloaded(file, path):
    for entry in os.listdir(path):
        if os.path.isfile(os.path.join(path, entry)):
            if file in entry:
                return True

def get_videos_urls(session, course):
    video_array = []

    # Get videos URLs
    response = session.get(course, cookies=COOKIES, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get course title
    course_title = soup.find('title').string

    print()
    print('Getting videos URLs from course: ' + course_title)

     # Iterate over the response and grab all the videos URLs
    for video in soup.find_all('a', {'class': 'text-base text-slate-900 dark:text-zinc-100'}):
        video_array.append(video.get('href'))

    return (course_title, video_array)

def downloader(session, video, folder):
    # keep track if the video has been downloaded
    video_downloaded = False

    # keep track of how many attempts to download the video
    attempts = 0

    # save directory
    save_dir = "videos/" + folder

    # Print status
    print()
    print('Getting video URL from: ' + video)

    # attempt to download the video
    while (not video_downloaded) and (attempts < 10):
        attempts += 1
        print("Attempt: " + str(attempts))

        try:
            video_url = BASE_URL + video
            video_response = session.get(video_url, cookies=COOKIES, headers=HEADERS, timeout=15)
            video_soup = BeautifulSoup(video_response.text, 'html.parser')

            if video_soup.find('h1', {'class': 'text-2xl font-semibold tracking-tight'}):
                print("Video skipped: Content Unavailable")
                break
            else:
                # Get the video id
                video_id = video_soup.find('div', {'class': 'aspect-w-16 aspect-h-9 relative z-20'}).get('data-vimeo-uid-value')

                if (not validate_video_id(video_id)):
                        raise Exception('Invalid video id')
                            
                # Get the video title
                video_title = video_soup.find('h2', {'class': 'text-2xl font-semibold tracking-tight text-slate-700 dark:text-zinc-100'}).text
                video_title = slugify(video_title)

                # Check if the video has already been downloaded
                if verify_downloaded(video_title + '.mp4', save_dir + '/'):
                    print("Video skipped: Already downloaded")
                    break

                # Get the video iframe response
                iframe_response = session.get(VIDEO_BASE_URL.replace('VIDEO_ID', video_id))

                # Grab the iframe source
                iframe_src = iframe_response.json()['html'].split('src="')[1].split('"')[0]

                print("Downloading...")

                # Added a timeout of 15 seconds on the download method of the Vimeo library
                downloader = Vimeo(iframe_src, embedded_on=video_url)
                downloader.streams[-1].download(download_directory=save_dir, filename=video_title)

                # Set the download flag to true
                video_downloaded = True

        except Exception as e:
            print("Retrying... " + str(e))
            continue

    if not video_downloaded and attempts == 10:
        print("Failed to download video")
        return video

    if video_downloaded:
        print("Video downloaded")

if __name__ == '__main__':
    session = requests.Session()

    for course in COURSES:
        course_URL = BASE_URL + course
        video_collection = get_videos_urls(session, course_URL)

        course_title = video_collection[0]
        video_array = video_collection[1]

        missed_videos = []

        for video in video_array:
            video = downloader(session, video, course_title)
            if video:
                missed_videos.append(video)

        while(len(missed_videos) > 0):
            for video in missed_videos:
                video = downloader(session, video, course_title)
                if video:
                    missed_videos.append(video)
    
