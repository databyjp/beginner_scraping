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
from bs4 import BeautifulSoup
import re


def scrape_this(uri="/pages/forms/"):

    page = requests.get("https://scrapethissite.com" + uri)
    soup = BeautifulSoup(page.text, "html.parser")

    # ========== GET A SIMPLE STAT ==========
    div = soup.find(id="hockey")  # Find the right div
    table = div.find("table")

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
    return data_df


page = requests.get("https://scrapethissite.com/pages/forms/")
soup = BeautifulSoup(page.text, "html.parser")
pagination = soup.find("ul", attrs={"class": "pagination"})
link_elms = pagination.find_all("li")
links = [link_elm.find("a").attrs["href"] for link_elm in link_elms]
links = set(links)

temp_dfs = list()
for link in links:
    tmp_df = scrape_this(uri=link)
    temp_dfs.append(tmp_df)
hockey_team_df = pd.concat(temp_dfs, axis=0).reset_index(drop=True)
hockey_team_df.sort_values(["year", "name"], inplace=True)
hockey_team_df.to_csv("hockey_team_df.csv")

# ===== Bonus content - simple visualisations =====
hockey_team_df.wins = hockey_team_df.wins.astype(int)
hockey_team_df.losses = hockey_team_df.losses.astype(int)
hockey_team_df = hockey_team_df.assign(win_pct=hockey_team_df.wins/(hockey_team_df.wins+hockey_team_df.losses))

import plotly.express as px
fig = px.scatter(
    hockey_team_df, x="gf", y="win_pct", color="name", template="plotly_white",
    title="Correlation between wins & goals scored",
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={"name": "Team", "gf": "Goals Scored", "win_pct": "Win Percentage"}
)
fig.show()

fig = px.scatter(
    hockey_team_df, x="ga", y="win_pct", color="name", template="plotly_white",
    title="Correlation between wins & goals allowed",
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={"name": "Team", "ga": "Goals Against", "win_pct": "Win Percentage"}
)
fig.show()

fig = px.scatter(
    hockey_team_df, x="diff", y="win_pct", color="name", template="plotly_white",
    title="Correlation between wins & goal differential",
    color_discrete_sequence=px.colors.qualitative.Safe,
    labels={"name": "Team", "diff": "Goal Differential", "win_pct": "Win Percentage"}
)
fig.show()

