import helpers
import pandas as pd
import sys
import mysql.connector
import datetime


from dotenv import load_dotenv
load_dotenv()

if len(sys.argv) < 3:
    print("No enough arguments")
    print("upload_azlyrics.py filename database")
    exit


filename = sys.argv[1]
database = sys.argv[2]

chunksize = 100
if len(sys.argv) > 3:
    chunksize = int(sys.argv[3])


columns = {
    'artist': 'ARTIST_NAME', 
    'song':'SONG_NAME', 
    'lyrics': 'LYRICS'
    }

mysql = helpers.Mysql(database_name=database)
mysql.open_connection()

def save_to_db(df):
    mysql.execute_insert_bulk(
        artist=df[columns['artist']].values,
        song=df[columns['song']].values,
        lyrics=df[columns['lyrics']].values,
        char_length=[x for x in df[columns['lyrics']].apply(lambda x: len(x))],
        created_on=df[columns['song']].apply(lambda x: datetime.datetime.now()).tolist()
    )

def save_row_to_db(artist, song, lyrics, char_length, created_on):
    mysql.execute(mysql.literal_insert_string, artist, song, lyrics, char_length, created_on)




chunk_no = 1
with pd.read_csv(filename, chunksize=chunksize) as reader:
    for chunk in reader:
        print(f"Uploading chunk {chunk_no}...")
        try:
            save_to_db(chunk)
        except:
            print("exception at chunk: {}".format(chunk_no))
            for index, row in chunk.iterrows():
                print("retrying index: {}".format(index))
                try:
                    save_row_to_db(row[columns['artist']],row[columns['song']],row[columns['lyrics']],
                               len(row[columns['lyrics']]),datetime.datetime.now())
                except:
                    print("Retry failed at index: {}".format(index))
        chunk_no += 1
    print(f"all chunks uploaded.")



