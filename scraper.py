
import re
import time
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
    'https://profissao-investidor.memberkit.com.br/12134-profissao-investidor-commodities',
    'https://profissao-investidor.memberkit.com.br/43922-renda-fixa-profissional',
    'https://profissao-investidor.memberkit.com.br/61479-operacao-de-ciclo-do-dolar'
]

# Cookie string
RAW_COOKIES = "menu=false; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3lOems1T1RjMVhTd2lKREpoSkRFeEpISmlhVGRRWWtWVlVrTlBVSGRPY0ZVeVlqQTJkeTRpTENJeE5qWTRPVE0wT0RVekxqSTJNemd6TVRZaVhRPT0iLCJleHAiOiIyMDIyLTEyLTA0VDA5OjAwOjUzLjI2M1oiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ==--41ea22ddea22b38ef6b299e59b1f3bd475ef4e32; _memberkit_session=UbD2lSs26qVQbGLTIcL2mUZPmKWDIvUZdfGmXIV5pSkkYnKFxuGbCfZR0gl1Wj4BU9aKkMFJghytRGJmWPT90PnOQvSG4Y0lcN559bVd4+EfXpO1DbTzpOWR20Fy47FCGmaKyLox7cPx4SNfUJseOkvJb7yLUpabj1GQpJ5MLEVM24H9F79dLDbWTuUza4MGsfx1zRNVatk0nOvMsgL+HHkL+imP1kBjGYOs/UiXBkuAJNjOKvnBzTWB+CPrYb7x9rJYzefdKKRQecem6B5v9L/kq+s+a5ighiwwQEOfLk1L4mcO1IefL0aCWjkmPMWjRokj2/UYuvdRtIpKeuorz8n2aL7kFsm5e2Rva0RLUpdcDnLSLTX6I0HkOAGcA0Ialkm6yervcVGq6TsD2oLNmt0kugzU7l1HiefuAMaNoJsmBFQmgzuTWHO1QhCYNu/On+OIS3HGWplXYyOkDiynu2monL8QEmOM5LxHQn9e8t4h7/ZJyMiJuU+/UNnJmML0KdbN/jE3PjsTjeQkSpAFyQQt--nBGMzUv/5hp/7ohs--B5DGlLIbhIsB57qIa2K9nQ=="

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

def get_videos_urls(session, course):
    videos_array = []

    # Get videos URLs
    response = session.get(course, cookies=COOKIES, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get course title
    course_title = soup.find('title').string

    print()
    print('Getting videos URLs from course: ' + course_title)

     # Iterate over the response and grab all the videos URLs
    for video in soup.find_all('a', {'class': 'text-base text-slate-900 dark:text-zinc-100'}):
        videos_array.append(video.get('href'))

    return (course_title, videos_array)

def downloader(session, videos_array, folder):
    # Iterate over videos
    for video in videos_array:
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
            time.sleep(5)

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
            missed_videos_array.append(video)

        if video_downloaded:
            print("Video downloaded")

    return missed_videos_array

if __name__ == '__main__':
    session = requests.Session()
    for course in COURSES:
        videos_array = get_videos_urls(session, course)[1]
        course_title = videos_array[0]

        missed_videos_array = downloader(session, videos_array, course_title)
        while(len(missed_videos_array) > 0):
            missed_videos_array = downloader(session, missed_videos_array)
    
