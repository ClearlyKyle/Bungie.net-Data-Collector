import pandas
from pandas import read_csv
from matplotlib import pyplot

series = read_csv('D3LTA ENF0RC3R_OUTPUT.csv',
                  parse_dates=True,
                  usecols=['date', 'skill level', 'playlist'])

series = series.dropna()

series['date'] = pandas.to_datetime(series["date"])

TS = series[series['playlist'] == 'Team Slayer'].sort_values(by="date", ascending=True)
TD = series[series['playlist'] == 'Team Doubles'].sort_values(by="date", ascending=True)

pyplot.figure(figsize=(10, 5))
pyplot.plot(TS['date'], TS['skill level'], label='TS')
pyplot.plot(TD['date'], TD['skill level'], label='TD')
pyplot.legend(loc='best')
pyplot.xticks(rotation=45)
pyplot.subplots_adjust(left=0.051, right=0.982, top=0.974, bottom=0.156)
pyplot.show()
