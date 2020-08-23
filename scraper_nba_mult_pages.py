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


out_dfs = list()
for yr in range(2001, 2021):
    page = requests.get("https://www.basketball-reference.com/leagues/NBA_" + str(yr) + ".html")
    soup = BeautifulSoup(page.text, "html.parser")
    tmp_df = scrape_team_stats(soup, "all_team-stats-per_poss")
    tmp_df = tmp_df.assign(season=yr)
    out_dfs.append(tmp_df)

per_poss_df = pd.concat(out_dfs, axis=0)

# ===== Bonus content - simple visualisations =====

import plotly.express as px
fig = px.scatter(
    per_poss_df, x="season", y="pts", color="name", template="plotly_white",
    title="Points per 100 Possessions<BR>by season & team",
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={'pts': "Points per 100 Possessions", "season": "Season"}
)
fig.show()

fig = px.scatter(
    per_poss_df, x="season", y="fg3a", color="name", template="plotly_white",
    title="3 Point Attempts per 100 Possessions<BR>by season & team",
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={'fg3a': "3PT Attempts per 100 Possessions", "season": "Season"}
)
fig.show()

fig = px.scatter(
    per_poss_df, x="season", y="fta", color="name", template="plotly_white",
    title="Free Throw Attempts per 100 Possessions<BR>by season & team",
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={'fta': "Free Throw Attempts per 100 Possessions", "season": "Season"}
)
fig.show()
