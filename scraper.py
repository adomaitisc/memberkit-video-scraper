# HTTP client
import time
import requests

# Cookie parser
from http.cookies import SimpleCookie

# HTML parser
from bs4 import BeautifulSoup

# Vimeo downloader
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
RAW_COOKIES = "remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3lOems1T1RjMVhTd2lKREpoSkRFeEpISmlhVGRRWWtWVlVrTlBVSGRPY0ZVeVlqQTJkeTRpTENJeE5qWTRPVEF4TURjekxqRTBOekV5TWpFaVhRPT0iLCJleHAiOiIyMDIyLTEyLTAzVDIzOjM3OjUzLjE0N1oiLCJwdXIiOiJjb29raWUucmVtZW1iZXJfdXNlcl90b2tlbiJ9fQ%3D%3D--192e9d63d4a1bdcd390cd4c031805215f74523bc; menu=false; _memberkit_session=nuO2wYfPOre%2B5TLL7pXENLM9wr48Ew6HRgmpaaTXRPbvsQ3A88jfOx3nzUL6nRy1pzK4M4QSXPKk8c99MDTDxTJPMwV84BXMRALYLNvf1zs6dw8yvZb2ZAwRZt%2F3ydokpfsZxZOGiFzOj9hyLnOYuX6Gy7buYoTvU1pwWR42nGTUSnLDMsAAeM%2FCZiCGuKMVw34yWu2zDVYA2%2Bheu1OlTFxOtkx4KANJjbe0mXmo9TMeTBo4ZjzfHVC6lSsq%2FzvTs2rkZON2GZk4BUIKraZbG5Ic%2B1VkrpHN%2Bv9pdUBCo9IcQmr7MTKQOx5CudeDxqoKYO06LrJvUZwrgEW%2BFpoNo4OfVh1Q1svdG23ybH%2BNDU6GncSIEk%2BAPt0hK9G92PgKaUCUTEMl3BluZo4390As7lLE5Uu34ogwruMAjyxBjC%2BGYPDxUovoApGAPBLQq8lwL8PuAeQ7Do24gXDuc%2Bqq741Z8aniHMANqrj%2FhwVB9Lpclwe4znFM3CO3E73PtJ%2BTvQLJVny%2FOKVgru9kXt9n96Ja--TfDWpSS3VEI5P%2FHg--jkOPwh9O01RStntvAmp6wQ%3D%3D"

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

# Iterate over courses
for course in COURSES:
    # Videos URLs
    VIDEOS = []

    # Get videos URLs
    session = requests.Session()
    response = session.get(course, cookies=COOKIES, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get course title
    course_title = soup.find('title').string

    print()
    print('Getting videos URLs from course: ' + course_title)

    # Iterate over the response and grab all the videos URLs
    for video in soup.find_all('a', {'class': 'text-base text-slate-900 dark:text-zinc-100'}):
        VIDEOS.append(video.get('href'))

    # Iterate over videos
    for video in VIDEOS:
        # keep track if the video has been downloaded
        video_downloaded = False

        # keep track of how many attempts to download the video
        attempts = 0

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
                    video_name = video_soup.find('h2', {'class': 'text-2xl font-semibold tracking-tight text-slate-700 dark:text-zinc-100'}).text

                    # Get the video iframe response
                    iframe_response = session.get(VIDEO_BASE_URL.replace('VIDEO_ID', video_id))

                    # Grab the iframe source
                    iframe_src = iframe_response.json()['html'].split('src="')[1].split('"')[0]

                    print("Downloading...")
                    # Added a timeout of 15 seconds on the download method of the Vimeo library
                    downloader = Vimeo(iframe_src, embedded_on=video_url)
                    downloader.streams[-1].download(download_directory='videos', filename=video_name)

                    # Set the download flag to true
                    video_downloaded = True
            except:
                print("Retrying...")
                time.sleep(20)
                continue

            if not video_downloaded and attempts == 5:
                print("Failed to download video")

