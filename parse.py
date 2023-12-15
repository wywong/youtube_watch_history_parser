from bs4 import BeautifulSoup
import os
import shutil

if os.path.isdir("output"):
    shutil.rmtree("output")

os.mkdir("output")

with open("watch-history.html") as watch_history:
    soup = BeautifulSoup(watch_history, "lxml")
    atags = soup.find_all('a')
    total_videos = dict()
    for atag in atags:
        href = atag["href"]
        if "youtube" in href:
            total_videos[href] = atag.text
    print("Total watched: %d" % len(total_videos))
    keys = total_videos.keys()
    with open("output/pruned.html", "w+") as pruned_html:
        pruned_html.write("<div style=\"display: flex;flex-direction: column;\">")
        pruned_html.write("\n")
        for key in keys:
            text = total_videos[key]
            if text != key:
                pruned_html.write("<a href=\"%s\">" % key)
                pruned_html.write("%s</a>" % text)
                pruned_html.write("\n")
        pruned_html.write("</div>")
