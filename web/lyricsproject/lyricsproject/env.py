import os
from dotenv import load_dotenv
load_dotenv()


def get_key(key, default_value = None):
    return os.getenv(key) or default_value