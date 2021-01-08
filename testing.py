import requests
import cchardet
import lxml
import time
import re
import csv
import pandas
from bs4 import BeautifulSoup

main_link = "http://halo.bungie.net/Stats/GameStatsHalo3.aspx?gameid=418174549&player=d3lta%20enf0rc3r"
raw_gamer_tag = "D3LTA ENF0RC3R"
results = []


def gameMode(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "lxml")

    game_played = soup.select(".first.styled")[0].getText().split(' on ')
    playlist = soup.select("li[class=styled]")[0].getText().split(" - ")[1].strip('\xa0')

    player_id = soup.findAll('a', {'href': '/Stats/Halo3/Default.aspx?player={}'.format(raw_gamer_tag)})[2]['id']
    player_id = player_id.replace('overview', 'kills')
    player_id = player_id.replace('hlGamertag', 'trPlayerRow')

    carnage_report = soup.find('tr', id=player_id)

    skill_level = carnage_report.select(".num")[0].getText()

    # Kills, Assists, Deaths, K/D Spread, Suicides, Betrayals
    KDA = [x.get_text() for x in carnage_report.find_all('td', class_="col")]

    # print("KDA = ", KDA)
    k, a, d, ks, s, b = KDA  # Suicides, Betrayals - not being used
    date = soup.select('.summary li')[3].get_text().strip(",").split()[0].strip(",")

    return {"game mode": game_played[0],
            "map": game_played[1],
            "playlist": playlist,
            "skill level": skill_level,
            "kills": k,
            "assists": a,
            "deaths": d,
            "date": date}


results.append(gameMode(main_link))

print([i for i in range(10)])

print(results)

'''
keys = list(results[0].keys())
print(keys)
with open('{}_OUTPUT.csv'.format(raw_gamer_tag), 'w', newline='') as output_file:  # You will need 'wb' mode in Python 2.x
    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    dict_writer.writeheader()
    for row in results:
        dict_writer.writerow(row)
'''
