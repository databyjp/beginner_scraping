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

# ===== START SCRAPING =====
import requests
from bs4 import BeautifulSoup, Comment

page = requests.get("https://www.basketball-reference.com/leagues/NBA_2020.html")
soup = BeautifulSoup(page.text, "html.parser")


def scrape_team_stats(soup_in, div_id="all_team-stats-per_game"):

    div = soup_in.find(id=div_id)
    comments = div.find_all(text=lambda text: isinstance(text, Comment))  # find hidden table
    if len(comments) > 0:
        div = BeautifulSoup(comments[0].extract(), "html.parser")

    # ========== PARSE EACH ROW OF DATA ==========
    data_rows = div.find_all("tr")  # Includes the header row!
    parsed_data = list()
    team_attr = {"data-stat": "team_name"}
    stat_keys = [col.attrs["data-stat"] for col in data_rows[0].find_all("th")]
    # stat_names = [col.attrs["aria-label"] for col in data_rows[0].find_all("th")]

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

    return data_df


per_gm_df = scrape_team_stats(soup, "all_team-stats-per_game")
opp_per_gm_df = scrape_team_stats(soup, "all_opponent-stats-per_game")
per_poss_df = scrape_team_stats(soup, "all_team-stats-per_poss")
