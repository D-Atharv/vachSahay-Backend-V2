import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client['vach-sahay']


def get_database():
    return db
