from bs4 import BeautifulSoup
from youtube_dl import YoutubeDL
import argparse
import csv
import glob
import os
import shutil
import time

DEFAULT_WATCH_HISTORY_HTML = "watch-history.html"
OUTPUT_DIR = "output"
WATCH_CSV_PATH = str(os.path.join(OUTPUT_DIR, "watch.csv"))
THUMBNAIL_DIR = "thumbnail_cache"

VIDEO_URL_KEY = "VIDEO_URL"
VIDEO_NAME_KEY = "VIDEO_NAME"
WATCH_DATE_KEY = "WATCH_DATE"

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


def valid_content(content_text):
    return content_text.startswith("Watched") \
        and not content_text.startswith("Watched a video that has been removed")

class WatchHistoryHTMLParser:
    def __init__(self,
                 watch_history_html=DEFAULT_WATCH_HISTORY_HTML):
        self.watch_history_html = watch_history_html

    def to_csv(self):
        with open(self.watch_history_html) as watch_history:
            soup = BeautifulSoup(watch_history, "lxml")
            atags = soup.find_all('a')
            total_videos = dict()

            contents = soup.select('div.content-cell')
            watched_divs = filter(lambda x: valid_content(x.text), contents)
            with open(WATCH_CSV_PATH, "w", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([VIDEO_URL_KEY, VIDEO_NAME_KEY, WATCH_DATE_KEY])
                for watched in watched_divs:
                    try:
                        atag = watched.find('a')
                        url = atag["href"]
                        video_name = atag.text
                        if video_name != url:
                            last_br = watched.find_all("br")[-1]
                            watch_date = ''.join(last_br.next_siblings)
                            csvwriter.writerow([url, video_name, watch_date])
                    except Exception as err:
                        print("FAILED TO PARSE %s", err)
                        print(watched)

    def to_pruned_html(self):
        if not os.path.exists(WATCH_CSV_PATH):
            self.to_csv()
        with open(WATCH_CSV_PATH, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            with open(OUTPUT_DIR + "/pruned.html", "w+") as pruned_html:
                pruned_html.write("<div style=\"display: flex;flex-direction: column;\">")
                pruned_html.write("\n")
                for row in reader:
                    text = row[VIDEO_NAME_KEY]
                    video_url = row[VIDEO_URL_KEY]
                    try:
                        download_thumbnail(video_url)
                        time.sleep(1)
                    except Exception as err:
                        print("Failed to get thumbnail: %s" % video_url)
                        print(err)
                    pruned_html.write("<a href=\"%s\">" % video_url)
                    pruned_html.write("%s</a>" % text)
                    pruned_html.write("\n")
                pruned_html.write("</div>")


args_parser = argparse.ArgumentParser()
args_parser.add_argument("--src",
                         help="Unmodified watch-history.html file",
                         type=str,
                         default=DEFAULT_WATCH_HISTORY_HTML)
args_parser.add_argument("--csv",
                         help="""
                              Extracts relevant information from watch-history.html
                              and stores it in %s
                              """ % WATCH_CSV_PATH,
                         action="store_true")
args_parser.add_argument("--clean",
                         help="Removes the output folder prior to parsing.",
                         action="store_true")

args = args_parser.parse_args()

if args.clean and os.path.isdir(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

watch_parser = WatchHistoryHTMLParser(args.src)
if args.csv:
    watch_parser.to_csv()
else:
    watch_parser.to_pruned_html()

