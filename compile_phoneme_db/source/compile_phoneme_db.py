import requests
from bs4 import BeautifulSoup
import requests 
from urllib.parse import urlparse
import os
import os.path
import sqlite3
import whisper_timestamped

cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../cache")
word_database_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../words.db")

libravox_pages = [
    "https://librivox.org/christmas-short-works-collection-2022-by-various/",
]


def download_libravox_webpage(url):
    source_audio_urls = []

    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    #urls = []
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


def init_database():
    con = sqlite3.connect(word_database_path)
    
    cur = con.cursor()
    
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='word'")
    if res.fetchall()[0] == 0:
        #Create table
        cur.execute("CREATE TABLE word(index int, word text, phonemes text, source text, wave_data blob)")
    
    
def process_audio(waveform, file_path):
    con = sqlite3.connect(word_database_path)
    
    cur = con.cursor()
    #Delete previous enties
    cur.execute("DELETE FROM word WHERE source = '" + file_path + "'")
    
    

def file_has_been_processed(file_path):
    con = sqlite3.connect(word_database_path)
    
    cur = con.cursor()
    #Delete previous enties
    res = cur.execute("SELECT count(*) FROM word WHERE source = '" + file_path + "'")
    print(res.fetchall())
    return res.fetchall()[0] > 0
    
    


for url in libravox_pages:
    download_libravox_webpage(url)




# sources = [
#     "https://www.archive.org/download/christmasshortworks2022_2212_librivox/cswc2022_animalschristmastree_peters_128kb.mp3",
#     "https://www.archive.org/download/christmasshortworks2022_2212_librivox/cswc2022_anniewilliesprayer_snow_128kb.mp3"    
    
# ]
