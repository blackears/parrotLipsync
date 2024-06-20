import requests
from bs4 import BeautifulSoup
import requests 
from urllib.parse import urlparse
import os
import os.path

cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../cache")

libravox_pages = [
    "https://librivox.org/christmas-short-works-collection-2022-by-various/",
]


def download_libravox_webpage(url):
    source_audio_urls = []

    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    urls = []
    for link in soup.find_all('a'):
        page_link = link.get('href')
        if page_link.endswith(".mp3"):
            
            url_parts = urlparse(page_link)
            file_path = completeName = os.path.join(cache_dir, url_parts.path[1:])
            file_path = os.path.abspath(file_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if not("_64kb" in file_path):
                continue

            print("Downloading to: " + file_path)
            source_audio_urls.append(page_link)
            
            if os.path.exists(file_path):
                continue
            
            response = requests.get(page_link)

            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print('File downloaded successfully')
            else:
                print('Failed to download file')
                
#    print(source_audio_urls)
    return source_audio_urls

for url in libravox_pages:
    download_libravox_webpage(url)




# sources = [
#     "https://www.archive.org/download/christmasshortworks2022_2212_librivox/cswc2022_animalschristmastree_peters_128kb.mp3",
#     "https://www.archive.org/download/christmasshortworks2022_2212_librivox/cswc2022_anniewilliesprayer_snow_128kb.mp3"    
    
# ]
