from bs4 import BeautifulSoup
from youtube_dl import YoutubeDL
import glob
import os
import shutil
import time

OUTPUT_DIR = "output"
THUMBNAIL_DIR = "thumbnail_cache"
if os.path.isdir(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.mkdir(OUTPUT_DIR)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def download_thumbnail(url):
    video_id = url.split('=')[-1]
    thumbnail_path = os.path.join(THUMBNAIL_DIR, video_id)
    ydl_opts = {
        'outtmpl': str(thumbnail_path),
        'writethumbnail': True,
        'skip_download': True
    }
    if not glob.glob("%s/%s.*" % (THUMBNAIL_DIR, video_id)):
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


with open("watch-history.html") as watch_history:
    soup = BeautifulSoup(watch_history, "lxml")
    atags = soup.find_all('a')
    total_videos = dict()
    for atag in atags:
        href = atag["href"]
        if "youtube" in href and "watch?v=" in href:
            total_videos[href] = atag.text
    print("Total watched: %d" % len(total_videos))
    keys = total_videos.keys()
    available_keys = list(filter(lambda key: key != total_videos[key], keys))
    with open(OUTPUT_DIR + "/pruned.html", "w+") as pruned_html:
        pruned_html.write("<div style=\"display: flex;flex-direction: column;\">")
        pruned_html.write("\n")
        for key in available_keys:
            text = total_videos[key]
            pruned_html.write("<a href=\"%s\">" % key)
            pruned_html.write("%s</a>" % text)
            pruned_html.write("\n")
        pruned_html.write("</div>")

    for key in available_keys:
        download_thumbnail(key)
        time.sleep(1)

