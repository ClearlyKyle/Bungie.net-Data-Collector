import numpy
import multiprocessing
import bs4
import requests
from time import gmtime, strftime, sleep
from _collections import defaultdict

raw_gamer_tag = 'Sneaky Wizard'  # ENTER GAMER TAG CASE SENSITIVE

gamer_tag = raw_gamer_tag.replace(" ", "%20")
root_url = 'http://halo.bungie.net'


# Gets URLs for match pages
def get_game_page_urls(i, z):
    response = requests.get(z + str(i))
    soup = bs4.BeautifulSoup(response.text, "lxml")
    return [a['href'] for a in soup.select('tbody a[href*=Stats]')]


def get_total_pages(z):
    response = requests.get(z + str(1))
    soup = bs4.BeautifulSoup(response.text, "lxml")
    max_page = soup.select('.rgWrap strong')[1].get_text()
    total_links = soup.select('.rgWrap strong')[0].get_text()
    print("Total Pages to scan :", max_page, 'Total Links to check :', total_links)
    return max_page


def calculate_time_played(data):
    seconds = 0

    for i in range(len(data)):
        if len(data[i]) > 8:
            data[i] = data[i].replace(data[i].split(':')[0], '00')
        seconds += int(data[i].split(':')[0]) * 3600 + int(data[i].split(':')[1]) * 60 + int(data[i].split(':')[2])

    dd = int(seconds) // 86400  # days
    hh = (int(seconds) // 3600) % 24  # hours
    mm = (int(seconds) // 60) % 60  # minutes
    ss = seconds - (int(seconds) // 60) * 60  # seconds
    return "\nPlay Time : %d days, %d hours, %d minutes and %d seconds" % (dd, hh, mm, ss)


def start_data_collecting(game_history_url, gmode):
    last_page = int(get_total_pages(game_history_url)) + 1

    myarray_kills = numpy.array([])
    myarray_assists = numpy.array([])
    myarray_deaths = numpy.array([])
    myarray_kd = numpy.array([])

    myarray_skill = numpy.array([])
    myarray_date = numpy.array([])

    game_duration = []
    maps_played = []

    print("-------- Collecting {} Game Data --------".format(gmode))

    # for i in range(1, 10):  # for testing
    for i in range(1, last_page):  # all games on bungie.net

        game_page_urls = get_game_page_urls(i, game_history_url)

        # sleep(1)

        pool = multiprocessing.Pool()
        results = pool.map(get_game_data, game_page_urls)
        pool.close()

        for k in range(len(results)):
            try:
                myarray_kills = numpy.append(myarray_kills, [numpy.array([results[k]['kills']])])
                myarray_assists = numpy.append(myarray_assists, [numpy.array([results[k]['assists']])])
                myarray_deaths = numpy.append(myarray_deaths, [numpy.array([results[k]['deaths']])])
                myarray_kd = numpy.append(myarray_kd, [numpy.array([results[k]['kd']])])
                myarray_skill = numpy.append(myarray_skill, [numpy.array([results[k]['skill']])])

                maps_played.append(results[k]['map'])
                game_duration.append(results[k]['duration'])

                myarray_date = numpy.hstack([myarray_date, numpy.array([results[k]['date'].strip(",")])])

            except KeyError:
                sleep(1)
                continue

    numpy.savetxt('{}_{}_duration.txt'.format(gmode, gamer_tag), game_duration, delimiter=",", fmt="%s")
    numpy.savetxt('{}_{}_date.txt'.format(gmode, gamer_tag), myarray_date, delimiter=" ", fmt="%s")
    numpy.savetxt('{}_{}_map.txt'.format(gmode, gamer_tag), maps_played, delimiter=" ", fmt="%s")

    print("\n-------- Analysing collected Data --------")

    total_kills, total_deaths, total_assists = 0, 0, 0

    most_kills, most_kills_url = 0, ''
    for p in range(0, len(myarray_kills), 2):
        total_kills += int(myarray_kills[p])
        if int(myarray_kills[p]) > most_kills:
            most_kills = int(myarray_kills[p])
            most_kills_url = myarray_kills[p + 1]

    most_deaths, most_deaths_url = 0, ''
    for p in range(0, len(myarray_deaths), 2):
        total_deaths += int(myarray_deaths[p])
        if int(myarray_deaths[p]) > most_deaths:
            most_deaths = int(myarray_deaths[p])
            most_deaths_url = myarray_deaths[p + 1]

    most_assists, most_assists_url = 0, ''
    for p in range(0, len(myarray_assists), 2):
        total_assists += int(myarray_assists[p])
        if int(myarray_assists[p]) > most_assists:
            most_assists = int(myarray_assists[p])
            most_assists_url = myarray_assists[p + 1]

    most_kd, lowest_kd, most_kd_url, lowest_kd_url = 0, 0, '', ''
    for p in range(0, len(myarray_kd), 2):
        if int(myarray_kd[p]) > most_kd:
            most_kd = int(myarray_kd[p])
            most_kd_url = myarray_kd[p + 1]
        elif int(myarray_kd[p]) < lowest_kd:
            lowest_kd = int(myarray_kd[p])
            lowest_kd_url = myarray_kd[p + 1]

    print("Total Kills: ", total_kills, ' Total Deaths: ', total_deaths, " Total Assists: ", total_assists)
    print(gmode, "KD: ", total_kills / total_deaths)
    print("Most Kills in a game:\t\t", most_kills, ": URL: ", most_kills_url)
    print("Most Deaths in a game:\t\t", most_deaths, ": URL: ", most_deaths_url)
    print("Most Assists in a game:\t\t", most_assists, ": URL: ", most_assists_url)
    print("Highest KD in one match:\t {}{}".format('+', most_kd), ": URL:", most_kd_url)
    print("Lowest KD in one match:\t\t", lowest_kd, ": URL:", lowest_kd_url)
    print("Highest Skills: ")

    highest_skills_data = {}

    for p in range(1, len(myarray_skill), 3):
        if myarray_skill[p - 1] == '':
            continue
        elif myarray_skill[p] in highest_skills_data:
            if int(myarray_skill[p - 1]) > int(highest_skills_data[myarray_skill[p]][0]):
                highest_skills_data[myarray_skill[p]] = [myarray_skill[p - 1], myarray_skill[p + 1]]
        else:
            highest_skills_data[myarray_skill[p]] = [myarray_skill[p - 1], myarray_skill[p + 1]]

    for k, d in highest_skills_data.items():
        print('\t', k, '{}'.format('\t' if len(k) > 10 else '\t\t\t'), d)

    print(calculate_time_played(game_duration))

    print("Total Times a map has been played :")
    temp_dict = defaultdict(int)

    for i in maps_played:
        temp_dict[i] += 1

    for k, d in temp_dict.items():
        print('\t', k, '{}'.format('\t' if len(k) > 9 else '\t\t'), d)


def get_game_data(game_page_url):
    collected_data = {}
    # sleep(0.5)

    response = requests.get(root_url + game_page_url)
    soup = bs4.BeautifulSoup(response.text, "lxml")

    try:
        # "ctl00_mainContent_bnetpgd_kills_ctl02_trPlayerRow" Where ct102 is position in leader board
        player_id = soup.findAll('a', {'href': '/Stats/Halo3/Default.aspx?player={}'.format(raw_gamer_tag)})[2]['id']
        player_id = player_id.replace('overview', 'kills')
        player_id = player_id.replace('hlGamertag', 'trPlayerRow')

        collected_data['kills'] = [soup.select('#{} .col'.format(player_id))[0].get_text(), root_url + game_page_url]
        collected_data['assists'] = [soup.select('#{} .col'.format(player_id))[1].get_text(), root_url + game_page_url]
        collected_data['deaths'] = [soup.select('#{} .col'.format(player_id))[2].get_text(), root_url + game_page_url]
        collected_data['kd'] = [soup.select('#{} .col'.format(player_id))[3].get_text(), root_url + game_page_url]

        collected_data['skill'] = [soup.select('#{} .num'.format(player_id))[0].get_text(), soup.select('.summary li')[2].get_text().split(' - ')[1].strip('\xa0'), root_url + game_page_url]
        collected_data['map'] = soup.select('.summary li')[0].get_text().split(' on ')[1]

        collected_data['date'] = soup.select('.summary li')[3].get_text().strip(",").split()[0]
        collected_data['duration'] = soup.select('.summary li')[4].get_text().split()[1]

    except IndexError:
        print("Broken url: ", root_url + game_page_url)

    return collected_data


if __name__ == '__main__':
    global_page = 0

    print('-' * 66)
    print('Collecting Data for : ', raw_gamer_tag)
    print('-' * 66)

    # Matchmaking : Ranked + Social
    print("Starting Time for Matchmaking data collecting:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    print('http://halo.bungie.net/stats/playerstatshalo3.aspx?player=' + gamer_tag + '&ctl00_mainContent_bnetpgl_recentgamesChangePage=1')
    start_data_collecting('http://halo.bungie.net/stats/playerstatshalo3.aspx?player=' + gamer_tag + '&ctl00_mainContent_bnetpgl_recentgamesChangePage=', 'Matchmaking')
    print("-------- Finished Matchmaking data:", strftime("%Y-%m-%d %H:%M:%S", gmtime()), "--------")

    print()

    '''
    # Custom Games
    print("Starting Time for Custom game data collecting:", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    start_data_collecting('http://halo.bungie.net/stats/playerstatshalo3.aspx?player=' + gamer_tag + '&cus=2&ctl00_mainContent_bnetpgl_recentgamesChangePage=', 'Custom')
    print("-------- Finished Custom data:", strftime("%Y-%m-%d %H:%M:%S", gmtime()), " --------")

    print()    
    '''

    print("Completed Data Collecting.")
