## Parse YouTube watch history

Extracts links to watched youtube videos from watch-history.html from google takeout.

# Setup

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install --upgrade pip`

`pip install -r requirements.txt`

## Usage

Run the command

`python parse.py`

Pruned html file with only links to watched videos will be written to `output/pruned.html`

# Options

`--clean` removes the `output` folder at the beginning

`--csv` generates only a csv with watch history info
* `VIDEO_URL` - url to the youtube video
* `VIDEO_NAME` - Title of the youtube video
* `WATCH_DATE` - The time the video was watched

