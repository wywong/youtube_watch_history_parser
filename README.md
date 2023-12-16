# Parse YouTube watch history

Extracts links to watched youtube videos from watch-history.html from google takeout.

## Setup

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install --upgrade pip`

`pip install -r requirements.txt`

## Usage

Run the command

`python parse.py`

Pruned html file with only links to watched videos will be written to `output/pruned.html`

Generate an image tiled with watched video thumbnails. Written to `output/tiled.png`

`python parse.py --mode tile --max-num-images 540 --start-date "2020-07-01" --end-date "2020-07-31" --clean --images-per-row 24 --tile-width 64 --tile-height 32 --unique`

### Options

`--clean` removes the `output` folder at the beginning

`--mode csv` generates only a csv with watch history info
* `VIDEO_URL` - url to the youtube video
* `VIDEO_NAME` - Title of the youtube video
* `WATCH_DATE` - The time the video was watched

`--mode prune` generates a pruned html with only links to the watched videos

`--mode tile` downloads the thumbnails associated with the watched videos and
              tiles them into one image

`--max-num-images` maximum number of thumbnails for the tiled image

`--start-date` only include videos watched on or after this date

`--end-date` only include videos watched on or before this date

`--images-per-row` number of thumbnails per row in the output image

`--tile-width` width in pixels for thumbnail tiles

`--tile-height` height in pixels for thumbnail tiles

`--unique` If a video has been watched multiple times, only include the latest watch
