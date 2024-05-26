import csv
import opendatasets as od
import pandas as pd
from . import helpers

AZLYRICS_URL = 'https://www.kaggle.com/datasets/albertsuarez/azlyrics/data' # 64mb

od.download(AZLYRICS_URL)

# load from folder

azlyrics = helpers.read_csv_max_split('./azlyrics/azlyrics-scraper/azlyrics_lyrics_a.csv')
azlyrics = pd.DataFrame(azlyrics[1:],columns=azlyrics[0])

# save azlyrics to csv on google drive
my_path = './azlyrics/azlyrics-scraper/'
full_data = []
helpers.read_csv_max_split_folder(my_path, lambda x: full_data.extend(x[1:]))
print("total files: {0}".format(len(full_data)))
full_data_df = pd.DataFrame(full_data, columns=azlyrics.columns)

print("total rows: {0}".format(len(full_data_df.index)))

# sanity check before saving
assert(len(full_data_df.iloc[full_data_df.index[~full_data_df['SONG_URL'].str.contains('www.azlyrics.com')]].index), 0)

full_data_df.to_csv('azlyrics.csv')