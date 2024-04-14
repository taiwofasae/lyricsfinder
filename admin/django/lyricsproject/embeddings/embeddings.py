from . import database
import json
import logging
from . import file_embeddings
from . import models

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

def get_openai_embeddings(phrases, model="text-embedding-3-small"):
    phrases = [text.replace("\n", " ") for text in phrases]
    return [d.embedding for d in client.embeddings.create(input = phrases, model=model).data]


API_VERSION = 'v2'

def api_version():
    return API_VERSION

def ping_db():
    return database.ping()


def create_embeddings_table():
    logging.info("Creating embeddings tables")

    database.execute(models.SongEmbedding.MysqlCommands.create_table())
    
    database.execute(models.PhraseEmbedding.MysqlCommands.create_table())

    database.execute(models.SearchEmbedding.MysqlCommands.create_table())
    
def get_phrase_id_if_exists(phrase):
    logging.info("Getting phrase details by id: {0}".format(phrase))

    results = database.fetch(models.PhraseEmbedding.MysqlCommands.get_phrase_id_if_exists(phrase))
    
    return results and results[0] and results[0][0]


def insert_or_update_phrase_embeddings(phrase, embeddings_vector):
    
    logging.info("Checking if phrase: '{0}' exists".format(phrase))        

    phrase_id = get_phrase_id_if_exists(phrase)

    logging.info("Inserting/updating phrase embeddings into file")
    if phrase_id:
        file_embeddings.save_phrase_embedding(phrase_id, embeddings_vector)

    

    try:
        
        logging.info("Inserting/updating phrase embeddings into database")

        embeddings_vec = []
        database.execute(models.PhraseEmbedding.MysqlCommands.update_embedding(phrase, embeddings_vec))
        
        database.execute(models.PhraseEmbedding.MysqlCommands.insert_embedding(phrase, embeddings_vec))
        
    except:
        pass
        #logging.error("failed insert_or_update_phrase_embeddings of phrase: '{0}'".format(phrase))

def insert_or_update_search_phrase_embeddings(search_id, search_phrase, embeddings_vector):
    

    logging.info("Inserting/updating search phrase embeddings into file")
        
    file_embeddings.save_search_phrase_embedding(search_id, embeddings_vector)


    try:
        

        
        logging.info("Inserting/updating search phrase embeddings into database")

        embeddings_vec = []
        database.execute(models.SearchEmbedding.MysqlCommands.update_embedding(search_id, embeddings_vec))
        
        database.execute(models.SearchEmbedding.MysqlCommands.insert_embedding(search_id, search_phrase, embeddings_vec))
        
    except:
        pass
        #logging.error("failed insert_or_update_phrase_embeddings of phrase: '{0}'".format(phrase))

    
        

def insert_or_update_song_embeddings(song_id, song_title, embeddings_vector):
    

    logging.info("Inserting/updating song embeddings into file")
    file_embeddings.save_song_embedding(song_id=song_id, embeddings=embeddings_vector)


    
    try:

        embeddings_vec = []
        logging.info("Inserting/updating song embeddings into database")
        database.execute(models.SongEmbedding.MysqlCommands.update_embedding(song_id, song_title, embeddings_vec))

        database.execute(models.SongEmbedding.MysqlCommands.insert_embedding(song_id, song_title, embeddings_vec))
    
    except:
        pass
        #logging.error("failed insert_or_update_song_embeddings of title: '{0}'".format(song_title))
        


def get_embeddings_for_song(song_id):
    logging.info("retreiving embedings for song_id: {0}".format(song_id))

    embedding = []

    logging.info("loading embedding from database")
    # load embedding from database
    results = database.fetch(models.SongEmbedding.MysqlCommands.get_embedding(song_id))
    if results:
        # deserialize json
        embedding = json.loads(results[0] and results[0][0])
        song_title = results[0] and results[0][1]

    if not embedding:
        logging.info("loading embedding from file")

        embedding = file_embeddings.load_song_embedding(song_id)
        if not results: # if there are no results, then insert song into database
            logging.info("saving embedding info to database")
            insert_or_update_song_embeddings(song_id, song_title, json.dumps([]))
    
    if not embedding:
        logging.info("fetching embedding from api")
        embedding = fetch_embeddings_for_songs([song_id])[0]

    return embedding


def get_embeddings_for_phrase(phrase):
    logging.info("retreiving embedings for phrase: '{0}'".format(phrase))

    embedding = []

    logging.info("Loading embedding from database")
    results = database.fetch(models.PhraseEmbedding.MysqlCommands.get_embedding(phrase))
    if results:
        # deserialize json
        phrase_id = results[0] and results[0][0]
        embedding = json.loads(results[0] and results[0][1])

        if not embedding:
            logging.info("loading embedding from file")
            embedding = file_embeddings.load_phrase_embedding(phrase_id)
        
        if not embedding:
            logging.info("fetching embedding from api")
            embedding = fetch_embeddings_for_phrases([phrase])[0]

    return embedding

def get_embeddings_for_search_phrase(search_id):
    logging.info("retreiving embedings for search phrase: '{0}'".format(search_id))

    embedding = []

    logging.info("Loading embedding from database")
    results = database.fetch(models.SearchEmbedding.MysqlCommands.get_embedding(search_id))
    if results:
        # deserialize json
        embedding = json.loads(results[0] and results[0][0])

    if not embedding:
        logging.info("loading embedding from file")
        embedding = file_embeddings.load_search_phrase_embedding(search_id)
    
    if not embedding:
        logging.info("fetching embedding from api")
        embedding = fetch_embeddings_for_search_phrases([search_id])[0]

    return embedding

def fetch_embeddings_for_song(song_id):
    

    embeddings = []
    logging.info("getting song details for song_id: '{0}'".format(song_id))
    results = database.fetch(models.Song.MysqlCommands.get_song(song_id))

    
    if results:
        (_ ,title, lyrics) = results[0]

        logging.info("getting openai embeddings for title: '{0}'".format(title))
        embeddings = get_openai_embeddings([lyrics])[0]

        logging.info("inserting/updating song embeddings")
        insert_or_update_song_embeddings(song_id, title, embeddings)

    return embeddings

def fetch_embeddings_for_songs(song_ids):

    return [fetch_embeddings_for_song(id) for id in song_ids]
    

    
def fetch_embeddings_for_phrases(phrases):
    logging.info("getting openai embeddings for {0} phrases".format(len(phrases)))
    embeddings = get_openai_embeddings(phrases)

    logging.info("saving embeddings")
    for phrase, embed in zip(phrases, embeddings):
        insert_or_update_phrase_embeddings(phrase, embed)

    return embeddings

def fetch_embeddings_for_search_phrase(search_id):

    embeddings = []

    logging.info("getting search phrase for search_id: '{0}'".format(search_id))
    results = database.fetch(models.Search.MysqlCommands.get_search(search_id))

    
    if results:
        phrase = results[0] and results[0][0]

        logging.info("getting openai embeddings for search phrase: '{0}'".format(phrase))
        embeddings = get_openai_embeddings([phrase])[0]

        logging.info("inserting/updating search phrase embeddings")
        insert_or_update_search_phrase_embeddings(search_id, phrase, embeddings)

    return embeddings


def fetch_embeddings_for_search_phrases(search_ids):
    logging.info("getting openai embeddings for {0} search phrases".format(len(search_ids)))

    return [fetch_embeddings_for_search_phrase(id) for id in search_ids]





if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    if ping_db():
        print("mysql database connection OK")
    else:
        print("mysql db unreachable :(")

#create_embeddings_table()
#insert_or_update_song_embeddings(3, "On the Low v2", [{"yes":2.0,"no":3.0}])
#phrase = 'Now imagine everyone'
#insert_or_update_phrase_embeddings(phrase, [{"yes":2.0,"no":3.0}])
#print(get_embeddings_for_phrase(phrase))
#fetch_embeddings_for_phrases(["On the low by burna boy"])

#print(get_phrase_id_if_exists('On the low by burna boy'))
