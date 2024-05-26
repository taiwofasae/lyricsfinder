import os
import csv
import mysql.connector


def mysql_insert_string(song, lyrics, char_length, created_on):

    return mysql_insert_bulk_string([song], [lyrics], [char_length], [created_on])

def mysql_insert_bulk_string(song, lyrics, char_length, created_on):
    insert_string = "INSERT INTO lyricsapp_song (title, lyrics, char_length, created_on) VALUES "

    for i in range(len(char_length)):
        insert_string += '("{0}","{1}",{2},{3}),'.format(
        song[i], lyrics[i], char_length[i], Mysql.to_db_time_format_str(created_on[i]))

    # remove trailing comma
    insert_string = insert_string[:-1] + ';'

    return insert_string

def csv_reader(filepath):
    output = []
    with open(filepath,"r") as file:
        reader = csv.reader(file)
        for line in reader:
            output.append(line)

    return output

def read_csv_max_split(filepath):
    output = []
    with open(filepath,"r") as file:
        for line in file:
            output.append([x.lstrip('\"').rstrip('\"') for x in line.rstrip().split('","',4)])

    return output

def read_csv_max_split_folder(folder, func):
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, f)):
            output = read_csv_max_split(os.path.join(folder, f))
            func(output)


def read_first_N_lines(filepath, cols=4, N=5):
    output = []
    with open(filepath,"r") as file:
        for i in range(N):
            line = next(file)
            output.append(line.rstrip())

    return output

from dotenv import load_dotenv
load_dotenv()


class Settings:
    def db(database_name, hostname):
        return {
            'USER': os.getenv('MYSQL_DB_USER'),
            'PASSWORD': os.getenv('MYSQL_DB_PASSWORD'),
            'HOST': hostname or os.getenv('MYSQL_DB_HOST'),
            'NAME': database_name or os.getenv('MYSQL_DB_NAME')
        }
    table_properties = {
        'id': 'int PRIMARY KEY auto_increment',
        'title': 'varchar(50) unique NOT NULL',
        'lyrics': 'longtext NOT NULL',
        'char_length': 'int',
        'created_on': 'datetime(6) NOT NULL',
    }
    table_name = 'lyricsapp_song'


class Mysql:
    def __init__(self, database_name = None, hostname = None) -> None:
        self.db = Settings.db(database_name, hostname)
        self.connection = None

    def open_connection(self, database_name = None, hostname = None):
        db = self.db
        self.connection = mysql.connector.connect(
            user=db['USER'],
            password=db['PASSWORD'],
            host=hostname or db['HOST'],
            database=database_name or db['NAME']
        )
        return self.connection


    def ping(self):

        try:
            cnx = self.open_connection()

            cnx.close()

        except:
            return False
        else:
            return True

    def to_db_time_format_str(timestamp):


        dt_format = "%Y-%m-%dT%H:%M:%S"
        db_format = "%Y-%m-%dT%H:%i:%s"

        db_time = f"str_to_date('{timestamp.strftime(dt_format)}', '{db_format}')"

        return db_time

    def execute(self, *args, **kwargs):
        cnx = self.open_connection()

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:

                result = cursor.execute(*args, **kwargs)

            cnx.commit()

            cnx.close()

    def execute_no_commit(self, *args, **kwargs):
        cnx = self.open_connection()

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:
                cursor.execute(*args, **kwargs)

    def execute_many(self, *args, **kwargs):
        cnx = self.open_connection()

        if cnx and cnx.is_connected():
            with cnx.cursor() as cursor:
                cursor.executemany(*args, **kwargs)

    def commit(self):
        print("committing...")
        if self.connection:
            if self.connection.is_connected():
                self.connection.commit()
            self.connection.close()
        else:
            print("connection object does not exist.")

    def escape_string(string):
        return string

    literal_insert_string = r"""
        INSERT INTO lyricsapp_song (title, lyrics, char_length, created_on) VALUES (%s,%s,%s,current_date());
        """
    def execute_insert_bulk(self, song, lyrics, char_length, created_on):
        
        self.execute_many(Mysql.literal_insert_string, [(s,l,c) for s,l,c in zip(song, lyrics, char_length)])

        self.commit()
