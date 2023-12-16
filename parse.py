from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
from youtube_dl import YoutubeDL
import argparse
import csv
import glob
import math
import os
import shutil
import time

DEFAULT_WATCH_HISTORY_HTML = "watch-history.html"
WATCH_HISTORY_DATE_FORMAT = "%b %d, %Y, %I:%M:%S %p %Z"
OUTPUT_DIR = "output"
WATCH_CSV_PATH = str(os.path.join(OUTPUT_DIR, "watch.csv"))
THUMBNAIL_DIR = "thumbnail_cache"
TILE_IMAGE_PATH = os.path.join(OUTPUT_DIR, "tiled.png")

VIDEO_URL_KEY = "VIDEO_URL"
VIDEO_NAME_KEY = "VIDEO_NAME"
WATCH_DATE_KEY = "WATCH_DATE"

MODE_PRUNE = "prune"
MODE_CSV = "csv"
MODE_TILE = "tile"

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
            time.sleep(1)
    return video_id


def valid_content(content_text):
    return content_text.startswith("Watched") \
        and not content_text.startswith("Watched a video that has been removed")

class WatchHistoryHTMLParser:
    def __init__(self,
                 watch_history_html,
                 start_date,
                 end_date):
        self.watch_history_html = watch_history_html
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    def to_csv(self):
        with open(self.watch_history_html) as watch_history:
            soup = BeautifulSoup(watch_history, "lxml")
            atags = soup.find_all('a')
            total_videos = dict()

            contents = soup.select('div.content-cell')
            watched_divs = filter(lambda x: valid_content(x.text), contents)
            date_format = WATCH_HISTORY_DATE_FORMAT
            with open(WATCH_CSV_PATH, "w", newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([VIDEO_URL_KEY, VIDEO_NAME_KEY, WATCH_DATE_KEY])
                row_count = 0
                for watched in watched_divs:
                    try:
                        atag = watched.find('a')
                        url = atag["href"]
                        video_name = atag.text
                        if video_name != url:
                            last_br = watched.find_all("br")[-1]
                            watch_date = ''.join(last_br.next_siblings)
                            d = datetime.strptime(watch_date, date_format).date()
                            if d >= self.start_date and d <= self.end_date:
                                csvwriter.writerow([url, video_name, watch_date])
                                row_count += 1
                    except Exception as err:
                        print("FAILED TO PARSE %s", err)
                        print(watched)
                print("Total csv rows: %s" % row_count)

    def to_tiled_image(self, max_images, imgs_per_row):
        if not os.path.exists(WATCH_CSV_PATH):
            self.to_csv()
        image_count = 0
        video_ids = []
        date_format = WATCH_HISTORY_DATE_FORMAT
        with open(WATCH_CSV_PATH, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                video_url = row[VIDEO_URL_KEY]
                try:
                    watch_date = datetime.strptime(row[WATCH_DATE_KEY], date_format)
                    video_id = download_thumbnail(video_url)
                    video_ids.append(video_id)
                    image_count += 1
                except Exception as err:
                    print("Failed to get thumbnail: %s" % video_url)
                    print(err)
                if image_count >= max_images:
                    break
        if len(video_ids) == 0:
            print("No watched videos found")
            return None
        print("Total images: %s" % image_count)
        imgs_per_col = int(math.ceil(float(image_count) / imgs_per_row))
        img_tile_width = 128
        img_tile_height = 72
        img_width = imgs_per_row * img_tile_width
        img_height = imgs_per_col * img_tile_height
        output_image = Image.new(mode="RGB", size=(img_width, img_height))
        r = 0
        c = 0
        for video_id in video_ids:
            video_path = glob.glob("%s/%s.*" % (THUMBNAIL_DIR, video_id))
            if len(video_path) > 0:
                img = Image.open(video_path[0]).copy()
                img.thumbnail((img_tile_width, img_tile_height))
                coord = (c * img_tile_width, r * img_tile_height)
                output_image.paste(img, coord)
                c += 1
                if c % imgs_per_row == 0:
                    c = 0
                    r += 1
        output_image.save(TILE_IMAGE_PATH)

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
                    pruned_html.write("<a href=\"%s\">" % video_url)
                    pruned_html.write("%s</a>" % text)
                    pruned_html.write("\n")
                pruned_html.write("</div>")


args_parser = argparse.ArgumentParser()
args_parser.add_argument("--src",
                         help="Unmodified watch-history.html file",
                         type=str,
                         default=DEFAULT_WATCH_HISTORY_HTML)
args_parser.add_argument("--mode",
                         help="""
                              prune - Creates a pruned down html file for watch
                                      history.
                              csv - Extracts relevant information
                                    from watch-history.html and stores it in %s
                              tile - Generates an image using thumbnails of
                                     watched videos
                              """ % WATCH_CSV_PATH,
                         type=str,
                         default=MODE_PRUNE)
args_parser.add_argument("--start-date",
                         help="""
                              Only include videos that were watched on or after
                              this date
                              """,
                         type=str,
                         default="1970-01-01")
args_parser.add_argument("--end-date",
                         help="""
                              Only include videos that were watched on or before
                              this date
                              """,
                         type=str,
                         default="9999-12-31")
args_parser.add_argument("--max-num-images",
                         help="Maximum number of thumbnails for the tiled image",
                         type=int,
                         default=210)
args_parser.add_argument("--images-per-row",
                         help="""
                              Number of thumbnails that will be pasted to each
                              row of the output image
                              """,
                         type=int,
                         default=7)
args_parser.add_argument("--tile-width",
                         help="""
                              Output width in pixels of the watched video
                              thumbnail tile
                              """,
                         type=int,
                         default=128)
args_parser.add_argument("--tile-height",
                         help="""
                              Output height in pixels of the watched video
                              thumbnail tile
                              """,
                         type=int,
                         default=72)
args_parser.add_argument("--clean",
                         help="Removes the output folder prior to parsing.",
                         action="store_true")

args = args_parser.parse_args()

if args.clean and os.path.isdir(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

watch_parser = WatchHistoryHTMLParser(args.src, args.start_date, args.end_date)
mode = args.mode
if mode == MODE_CSV:
    watch_parser.to_csv()
elif mode == MODE_TILE:
    watch_parser.to_tiled_image(args.max_num_images, args.images_per_row)
elif mode == MODE_PRUNE:
    watch_parser.to_pruned_html()
else:
    print("Unsupported mode: %s" % args.mode)

