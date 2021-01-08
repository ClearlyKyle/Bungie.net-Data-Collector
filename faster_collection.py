import requests
import re
import time
import concurrent.futures
import queue
import csv
import cchardet
import lxml
from bs4 import BeautifulSoup


def getMainLink(tag):
    '''
    :param tag: gamertag of account to get
    :return: url to pages that contain all games
    '''
    tag = tag.replace(" ", "%20")
    return "http://halo.bungie.net/stats/playerstatshalo3.aspx?player={}&ctl00_mainContent_bnetpgl_recentgamesChangePage=".format(
        tag)


def getNumberOfMatchMakingPages(link):
    '''
    :param link: link to first page of game history
    :return: number of pages (int)
    '''
    response = requests.get(link + "1")
    soup = BeautifulSoup(response.text, "lxml")
    return int(soup.select(".rgWrap.rgInfoPart strong")[1].get_text())


def getLinksToGamePages(link):
    f = requests.get(link)
    soup = BeautifulSoup(f.content, 'lxml')
    game_pages_QUEUE.put([i.get('href') for i in
                          soup.find_all('a',
                                        {"id": re.compile("mainContent"), "href": re.compile("Stats/GameStatsHalo3")})])


def gamePageDataCollection(link):
    '''
    Collecting data from a game page, anything that needs to be collected should be
    parsed here then returned in the dictionary
    :param link: game page url
    :return: dictionary of data needed
    '''
    page_url = "http://halo.bungie.net" + link
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "lxml")

    game_played = soup.select(".first.styled")[0].getText().split(' on ')
    playlist = soup.select("li[class=styled]")[0].getText().split(" - ")[1].strip('\xa0')

    player_id = soup.findAll('a', {'href': '/Stats/Halo3/Default.aspx?player={}'.format(gamertag)})[2]['id']
    player_id = player_id.replace('overview', 'kills')
    player_id = player_id.replace('hlGamertag', 'trPlayerRow')

    carnage_report = soup.find('tr', id=player_id)

    skill_level = carnage_report.select(".num")[0].getText()

    # Kills, Assists, Deaths, K/D Spread, Suicides, Betrayals
    KDA = [x.get_text() for x in carnage_report.find_all('td', class_="col")]

    k, a, d, ks, s, b = KDA  # Suicides, Betrayals - not being used
    date = soup.select('.summary li')[3].get_text().strip(",").split()[0].strip(",")

    page_data_QUEUE.put({"game mode": game_played[0],
                         "map": game_played[1],
                         "playlist": playlist,
                         "skill level": skill_level,
                         "kills": k,
                         "assists": a,
                         "deaths": d,
                         "date": date,
                         "url": page_url})


game_pages_QUEUE = queue.Queue()
page_data_QUEUE = queue.Queue()

gamertag = "D3LTA ENF0RC3R"

if __name__ == '__main__':

    print("Starting Collection\n")
    total_time_start = time.perf_counter()

    main_link = getMainLink(gamertag)
    number_of_pages = getNumberOfMatchMakingPages(main_link)

    start_timer = time.perf_counter()

    # Generate links to all the pages
    list_of_page_URLS = [main_link + str(i) for i in range(1, number_of_pages + 1)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(getLinksToGamePages, list_of_page_URLS)

    game_pages_LIST = []
    while not game_pages_QUEUE.empty():
        for link in game_pages_QUEUE.get():
            game_pages_LIST.append(link)

    print("Game Pages collected", len(game_pages_LIST))
    print("All game LINKS collected ({:.4f} seconds)".format(time.perf_counter() - start_timer))

    print()
    print("> Analysing games")

    game_data_LIST = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(gamePageDataCollection, game_pages_LIST)

    while not page_data_QUEUE.empty():
        game_data_LIST.append(page_data_QUEUE.get())

    print()
    print("All game DATA collected ({:.4f} seconds)".format(time.perf_counter() - start_timer))

    print("Writing all DATA to a CSV")

    keys = list(game_data_LIST[0].keys())
    with open('{}_OUTPUT.csv'.format(gamertag), 'w',
              newline='') as output_file:  # You will need 'wb' mode in Python 2.x
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        for row in game_data_LIST:
            dict_writer.writerow(row)

    print()
    print("Finished ({:.4f} seconds)".format(time.perf_counter() - total_time_start))
