import pandas, numpy
from pandas import read_csv
from matplotlib import pyplot

gamer_tag = "Sneaky Wizard"

series = read_csv('{}_OUTPUT.csv'.format(gamer_tag), parse_dates=True, converters={'players': eval})

print(series.columns.tolist())


print(series.explode('players')['players'].value_counts())


exit()
series['date'] = pandas.to_datetime(series["date"])

games_per_day = series['date'].value_counts().sort_index()
games_per_month = series.set_index('date').resample('MS').size()
games_per_year = series.set_index('date').resample('YS').size()

# print(games_per_day)
# print(games_per_month)
# print(games_per_year)
kd_spread_per_month = series.resample('MS', on='date')['spread'].sum()
average_spread_per_month = series.resample('MS', on='date')['spread'].mean()

# series = series.dropna()


playlists = series['playlist'].unique()
pyplot.figure(figsize=(10, 5))
for game_mode in playlists:
    game = series[series['playlist'] == game_mode].sort_values(by="date", ascending=True)
    pyplot.plot(game['date'], game['skill level'], label=game_mode)

pyplot.legend(bbox_to_anchor=(1, 1.02))
pyplot.xticks(rotation=45)
pyplot.title(gamer_tag)
pyplot.yticks(numpy.arange(0, 51, step=2))
pyplot.ylim([0, 51])
pyplot.grid()
pyplot.subplots_adjust(left=0.051, right=0.790, top=0.940, bottom=0.156)
pyplot.show()

fig = pyplot.figure()
gs = fig.add_gridspec(3, hspace=0)
axs = gs.subplots()
fig.suptitle('Games played')
axs[0].plot(games_per_year, 'o')
axs[1].plot(games_per_month)
axs[2].plot(games_per_day)
axs[2].sharex(axs[1])
pyplot.xticks(rotation=45)

for ax in axs:
    ax.label_outer()
pyplot.show()

# pyplot.plot(kd_spread_per_month)
pyplot.plot(average_spread_per_month)
pyplot.show()
