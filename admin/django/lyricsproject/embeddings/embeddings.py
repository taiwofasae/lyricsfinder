import database
import json
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

def get_openai_embedding(phrases, model="text-embedding-3-small"):
    phrases = [text.replace("\n", " ") for text in phrases]
    return client.embeddings.create(input = phrases, model=model).data[0].embedding

API_VERSION = 'v2'

def api_version():
    return API_VERSION

embeddings_folder = './embeds/'
song_folder = embeddings_folder+'song/'
phrase_folder = embeddings_folder+'phrase/'
def save_song_embedding_to_file(song_id, embeddings):
    
    with open("{0}{1}.csv".format(song_folder, song_id), 'w') as f:
        json.dump(embeddings, f, ensure_ascii=False)

def load_song_embedding_from_file(song_id):
    
    embeddings = []
    try:
        with open("{0}{1}.csv".format(song_folder, song_id), 'r') as f:
            embeddings = json.load(f)
    except:
        pass

    return embeddings

def save_phrase_embedding_to_file(phrase_id, embeddings):
    
    with open("{0}{1}.csv".format(phrase_folder, phrase_id), 'w') as f:
        json.dump(embeddings, f, ensure_ascii=False)

def load_phrase_embedding_from_file(phrase_id):
    
    embeddings = []

    try:
        with open("{0}{1}.csv".format(phrase_folder, phrase_id), 'r') as f:
            embeddings = json.load(f)
    except:
        pass
    return embeddings

def ping_db():
    return database.ping()


def similarity_score(search_string, song_id):

    return 0

def create_embeddings_table():
    logging.info("Creating embeddings tables")

    database.execute("""
    CREATE TABLE lyricsapp_song_embeddings (
                     song_id int PRIMARY KEY,
                     song_title varchar(50) NOT NULL,
                     serialized_embeddings longtext,
                     foreign key (song_id) references lyricsapp_song(id)
    );
""")
    
    database.execute("""
    CREATE TABLE lyricsapp_phrase_embeddings (
                     id int(11) not null PRIMARY KEY auto_increment,
                     phrase varchar(50) NOT NULL,
                     serialized_embeddings longtext,
                     CONSTRAINT phrase_unique UNIQUE (phrase)
    );
""")
    
def get_phrase_id_if_exists(phrase):
    logging.info("Getting phrase details by id: {0}".format(phrase))

    results = database.fetch("""
    SELECT id from lyricsapp_phrase_embeddings where phrase = "{0}";
""".format(phrase))
    
    return results and results[0] and results[0][0]


def insert_or_update_phrase_embeddings(phrase, embeddings_vector):
    

    logging.info("Inserting/updating phrase embeddings into database")
    
    

    try:
        embeddings_vec = []
        database.execute("""
    UPDATE lyricsapp_phrase_embeddings SET serialized_embeddings = '{1}' WHERE phrase = '{0}';
""".format(phrase, embeddings_vec))
        
        database.execute("""
    INSERT INTO lyricsapp_phrase_embeddings (phrase, serialized_embeddings) VALUES ('{0}','{1}');
""".format(phrase, embeddings_vec))
        
    except:
        pass

    phrase_id = get_phrase_id_if_exists(phrase)
    if phrase_id:
        save_phrase_embedding_to_file(phrase_id, embeddings_vector)
        

def insert_or_update_song_embeddings(song_id, song_title, embeddings_vector):
    

    

    logging.info("Inserting/updating song embeddings into database")
    try:
        logging.info("Inserting/updating song embeddings into file")
        save_song_embedding_to_file(song_id=song_id, embeddings=embeddings_vector)

        embeddings_vector = []

        database.execute("""
            UPDATE lyricsapp_song_embeddings SET song_title = '{1}', serialized_embeddings = '{2}' WHERE song_id = {0};;
        """.format(song_id, song_title, embeddings_vector))

        database.execute("""
    INSERT INTO lyricsapp_song_embeddings (song_id, song_title, serialized_embeddings) VALUES ({0},'{1}','{2}');
""".format(song_id, song_title, embeddings_vector))
    
    except:
        pass
        


def get_embeddings_for_song(song_id):
    logging.info("retreiving embedings for song_id: {0}".format(song_id))

    return load_song_embedding_from_file(song_id)
    results = database.fetch("""
    SELECT serialized_embeddings from lyricsapp_song_embeddings where song_id = {0};
""".format(song_id))
    
    return [json.loads(x[0]) for x in results]

def get_embeddings_for_phrase(phrase):
    logging.info("retreiving embedings for phrase: '{0}'".format(phrase))

    results = database.fetch("""
    SELECT id, serialized_embeddings from lyricsapp_phrase_embeddings where phrase = '{0}';
""".format(phrase))
    
    return [load_phrase_embedding_from_file(x[0]) for x in results]
    
    return [json.loads(x[0]) for x in results]

def fetch_embeddings_for_songs(song_ids):

    output = []

    for id in song_ids:
        results = database.fetch("""
    SELECT id, title, lyrics from lyricsapp_song where id = '{0}';
""".format(id))
        
        

        if results:
            (_ ,title, lyrics) = results[0]

            embeddings = get_openai_embedding([lyrics])
    
            insert_or_update_song_embeddings(id, title, embeddings)

            output += [embeddings]

    return output
    

    
def fetch_embeddings_for_phrases(phrases):
    embeddings = get_openai_embedding(phrases)
    for phrase, embed in zip(phrases, embeddings):
        insert_or_update_phrase_embeddings(phrase, embed)

    return embeddings

def refresh_embeddings_for_song(song_id):
    embeddings = get_embeddings_for_song(song_id)

    if not embeddings:
        embeddings = fetch_embeddings_for_songs([song_id])

    return embeddings

def refresh_embeddings_for_phrase(phrase):
    embeddings = get_embeddings_for_phrase(phrase)

    if not embeddings:
        embeddings = fetch_embeddings_for_phrases([phrase])

    return embeddings



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

refresh_embeddings_for_song(1)
refresh_embeddings_for_song(2)
refresh_embeddings_for_song(3)