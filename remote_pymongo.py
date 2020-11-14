#!/usr/bin/python

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
from pprint import pprint
from getpass import getpass

MONGO_HOST = "cs1.ncf.edu"
MONGO_DB = "hfmil"
MONGO_USER = input("Enter your username: ")
MONGO_PASS = getpass("Enter your password: ")

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', 27017)
)

server.start()

client = MongoClient('127.0.0.1', server.local_bind_port)

db = client[MONGO_DB]

# Prints the collection names
pprint(db.collection_names())

server.stop()
server.is_active
