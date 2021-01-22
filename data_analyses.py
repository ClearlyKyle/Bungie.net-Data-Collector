import pandas, numpy
from pandas import read_csv
from matplotlib import pyplot
from matplotlib.offsetbox import AnchoredText

gamer_tag = "Clearly Im KyLe"

pandas.set_option('display.max_rows', None)
series = read_csv('{}_OUTPUT.csv'.format(gamer_tag),
                  parse_dates=True,
                  converters={'players': eval})

# ['game mode', 'map', 'playlist', 'skill level', 'kills', 'assists', 'deaths', 'spread', 'players', 'date', 'url']
print(series.columns.tolist())
series['date'] = pandas.to_datetime(series["date"])

all_days = pandas.date_range(min(series['date']), max(series['date']), freq='D')

temp_series = series.copy()
temp_series.index = pandas.DatetimeIndex(series['date']).floor('D')
new_df = series.join(all_days.to_frame(), how='outer').drop(0, 1)

missing_dates_series = new_df.reset_index()

most_played_with = series.explode('players')['players'].value_counts()[1:15].to_frame().reset_index()

KD_spread_analysis = series['spread'].describe()
print(series.iloc[series['kills'].argmax()])
print(KD_spread_analysis)

games_per_day = missing_dates_series['date'].value_counts().sort_index()
games_per_month = missing_dates_series.set_index('date').resample('MS').size()
games_per_year = missing_dates_series.set_index('date').resample('YS').size()

kd_spread_per_month = series.resample('MS', on='date')['spread'].sum()
average_spread_per_month = series.resample('MS', on='date')['spread'].mean()

playlists = series['playlist'].unique()
pyplot.figure(figsize=(13, 5))
pyplot.plot([], [], label="Playlist", linewidth=0)
for game_mode in playlists:
    game = series[series['playlist'] == game_mode].sort_values(by="date", ascending=True)
    pyplot.plot(game['date'], game['skill level'], label=game_mode)

pyplot.legend(bbox_to_anchor=(1, 1.02))
pyplot.xticks(rotation=45)
pyplot.title(gamer_tag)
pyplot.yticks(numpy.arange(0, 51, step=2))
pyplot.ylim([0, 51])
pyplot.grid()

player_names = '\n'.join(most_played_with['index'].to_list())
player_name_count = '\n'.join(str(x) for x in most_played_with['players'])
box_pos = [1.24, 0.99]
ax = pyplot.gca()

max_kills = series.iloc[series['kills'].argmax()]

pyplot.text(x=box_pos[0], y=box_pos[1], s=player_names, ha='left', va='top', transform=ax.transAxes)
pyplot.text(x=box_pos[0] + 0.2, y=box_pos[1], s=player_name_count, ha='left', va='top', transform=ax.transAxes)
pyplot.subplots_adjust(left=0.070, right=0.700, top=0.940, bottom=0.156)
pyplot.show()


fig = pyplot.figure(figsize=(13, 5))
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
pyplot.figure(figsize=(13, 5))
pyplot.plot(average_spread_per_month)
pyplot.show()

