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
from bs4 import BeautifulSoup, Comment

page = requests.get("https://www.basketball-reference.com/leagues/NBA_2020.html")
soup = BeautifulSoup(page.text, "html.parser")

# ========== GET A SIMPLE STAT ==========
table = soup.find(id="confs_standings_E")  # Find the right table
team_elms = table.find_all("th", attrs={"data-stat" : "team_name"})
team_names = [team_elm.find("a").text for team_elm in team_elms if team_elm.find("a") is not None]

# ========== SCRAPE AN ENTIRE TABLE ==========
data_rows = table.find_all("tr")  # Includes the header row!
parsed_data = list()
team_attr = {"data-stat" : "team_name"}
stat_keys = [col.attrs["data-stat"] for col in data_rows[0].find_all("th")]
stat_names = [col.attrs["aria-label"] for col in data_rows[0].find_all("th")]

for row in data_rows:
    tmp_data = dict()
    if row.find(attrs=team_attr).find("a") is not None:
        team_link = row.find(attrs=team_attr).find("a").attrs["href"]
        tmp_data["name"] = row.find(attrs=team_attr).find("a").text
        for attr in stat_keys[2:]:
            tmp_data[attr] = row.find(attrs={"data-stat": attr}).text
        tmp_data["link"] = team_link
        parsed_data.append(tmp_data)

data_df = pd.DataFrame(parsed_data)

# ========== SCRAPE AN ENTIRE, HIDDEN TABLE ==========
# Find the right table
div = soup.find(id="all_team-stats-per_game")
comments = div.find_all(text=lambda text: isinstance(text, Comment))  # find hidden table
if len(comments) > 0:
    div = BeautifulSoup(comments[0].extract(), "html.parser")

# Get team name / links
team_elms = div.find_all(attrs={"data-stat" : "team_name"})  # This includes headers - we just want <td>
team_elms = div.find_all("td", attrs={"data-stat" : "team_name"})
teams_names = [team_elm.find("a").text for team_elm in team_elms if team_elm.find("a") is not None]
teams_links = [team_elm.find("a").attrs["href"] for team_elm in team_elms if team_elm.find("a") is not None]

# Get teams' points per game
pts_elms = table.find_all("td", attrs={"data-stat" : "pts"})
pts_list = [pts_elm.text for pts_elm in pts_elms]

# Zip team names & ppg
team_ppg = {k: v for k, v in zip(teams_names, pts_list[:30])}

# ========== PARSE EACH ROW OF DATA ==========
data_rows = div.find_all("tr")  # Includes the header row!
parsed_data = list()
team_attr = {"data-stat" : "team_name"}
stat_keys = [col.attrs["data-stat"] for col in data_rows[0].find_all("th")]
stat_names = [col.attrs["aria-label"] for col in data_rows[0].find_all("th")]

for row in data_rows:
    tmp_data = dict()
    if row.find(attrs=team_attr).find("a") is not None:
        team_link = row.find(attrs=team_attr).find("a").attrs["href"]
        tmp_data["name"] = row.find(attrs=team_attr).find("a").text
        for attr in stat_keys[2:]:
            tmp_data[attr] = row.find(attrs={"data-stat": attr}).text
        tmp_data["link"] = team_link
        parsed_data.append(tmp_data)

data_df = pd.DataFrame(parsed_data)
