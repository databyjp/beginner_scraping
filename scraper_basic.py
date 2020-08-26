# ========== (c) JP Hwang 22/8/20  ==========

import logging

# ===== START LOGGER =====
logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
root_logger.addHandler(sh)

import pandas as pd

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

# ===== START SCRAPING =====
import requests
from bs4 import BeautifulSoup
import re

page = requests.get("https://scrapethissite.com/pages/forms/")
soup = BeautifulSoup(page.text, "html.parser")

# ========== GET A SIMPLE STAT ==========
div = soup.find(id="hockey")  # Find the right div
table = div.find("table")

team_elm = table.find("tr", attrs={"class": "team"})
team_name = team_elm.find("td", attrs={"class": "name"}).text
team_name = re.sub(r"^\s+|\s+$", "", team_name)

# ========== SCRAPE AN ENTIRE TABLE ==========
data_rows = table.find_all("tr", attrs={"class": "team"})  # Includes the header row!
parsed_data = list()
stat_keys = [col.attrs["class"][0] for col in data_rows[0].find_all("td")]

for row in data_rows:
    tmp_data = dict()
    for attr in stat_keys:
        attr_val = row.find(attrs={"class": attr}).text
        tmp_data[attr] = re.sub(r"^\s+|\s+$", "", attr_val)
    parsed_data.append(tmp_data)

data_df = pd.DataFrame(parsed_data)
