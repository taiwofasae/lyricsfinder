import os
from dotenv import load_dotenv
load_dotenv()


def get_key(key, default_value = None):
    return os.getenv(key) or default_value

def get_int_key(key, default_value = None):
    val = get_key(key, '').strip()

    return int(val) if val.isdecimal() else default_value