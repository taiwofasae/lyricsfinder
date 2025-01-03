import mysql.connector
from common import log
from lyricsproject import settings

db = settings.DATABASES['default']

def open_connection():
    return mysql.connector.connect(
        user=db['USER'],
        password=db['PASSWORD'],
        host=db['HOST'],
        database=db['NAME']
    )


def ping():
    
    try:
        cnx = open_connection()

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

def execute(command, *args, **kwargs):
    log.info('execute:{0}'.format(command))
    cnx = open_connection()

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:

            result = cursor.execute(command, *args, **kwargs)

            cnx.commit()

        cnx.close()


def fetch(command, *args, **kwargs):
    log.info('fetch:{0}'.format(command))
    cnx = open_connection()

    output = []
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:

            result = cursor.execute(command, *args, **kwargs)

            rows = cursor.fetchall()

            for row in rows:
                output.append(row)

        cnx.close()

    else:
        print("Could not connect to database")

    return output