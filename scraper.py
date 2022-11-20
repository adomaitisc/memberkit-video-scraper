# HTTP client
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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Cookie': RAW_COOKIES,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

# HTTP iframe headers
IFRAME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Host': 'vimeo.com',
    'Origin': 'https://profissao-investidor.memberkit.com.br',
    'Referer': 'https://profissao-investidor.memberkit.com.br/',
    'sec-ch-ua': '"Chromium";v="95", "Google Chrome";v="95", ";Not A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}

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
        while (not video_downloaded) and (attempts < 5):
            video_url = BASE_URL + video
            video_response = session.get(video_url, cookies=COOKIES, headers=HEADERS)
            video_soup = BeautifulSoup(video_response.text, 'html.parser')

            # Skip the unavailable videos
            if video_soup.find('h1', {'class': 'text-2xl font-semibold tracking-tight'}):
                print("Video skipped: Content Unavailable")
                break
            else:
                # increment the attempts
                attempts += 1

                try:
                    # Get the video id
                    video_id = video_soup.find('div', {'class': 'aspect-w-16 aspect-h-9 relative z-20'}).get('data-vimeo-uid-value')

                    # Get the video title
                    video_name = video_soup.find('h2', {'class': 'text-2xl font-semibold tracking-tight text-slate-700 dark:text-zinc-100'}).text

                    # Get the video iframe response
                    iframe_response = session.get(VIDEO_BASE_URL.replace('VIDEO_ID', video_id))

                    # Grab the iframe source
                    iframe_src = iframe_response.json()['html'].split('src="')[1].split('"')[0]

                    print("Downloading...")
                    downloader = Vimeo(iframe_src, embedded_on=video_url)
                    downloader.streams[-1].download(download_directory='videos', filename=video_id)

                    # Set the download flag to true
                    video_downloaded = True
                except:
                    print("Retrying...")
                    continue

            if not video_downloaded and attempts == 5:
                print("Failed to download video")

