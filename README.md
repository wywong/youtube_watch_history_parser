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

