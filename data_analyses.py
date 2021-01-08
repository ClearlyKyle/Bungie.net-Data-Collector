import pandas, numpy
from pandas import read_csv
from matplotlib import pyplot

gamer_tag = "D3LTA ENF0RC3R"

series = read_csv('{}_OUTPUT.csv'.format(gamer_tag),
                  parse_dates=True,
                  usecols=['date', 'skill level', 'playlist'])

series = series.dropna()

series['date'] = pandas.to_datetime(series["date"])

playlists = series['playlist'].unique()
print(playlists)

pyplot.figure(figsize=(10, 5))
for game_mode in playlists:
    game = series[series['playlist'] == game_mode].sort_values(by="date", ascending=True)
    pyplot.plot(game['date'], game['skill level'], label=game_mode)

pyplot.legend(bbox_to_anchor=(1, 1.02))
pyplot.xticks(rotation=45)
pyplot.title(gamer_tag)
pyplot.yticks(numpy.arange(0, 51, step=2))
pyplot.ylim([0, 50])
pyplot.grid()
pyplot.subplots_adjust(left=0.051, right=0.790, top=0.940, bottom=0.156)
pyplot.show()
