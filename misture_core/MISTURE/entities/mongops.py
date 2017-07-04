#!/usr/bin/env python3
# encoding: utf-8

from pymongo.errors import ConnectionFailure
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient

from settings.const import ConfiguracionGlobal


def borrardb():

    # Conexion a local
    client = MongoClient()
    
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        db = Database(client=client,
                      name=ConfiguracionGlobal.MONGODB)
    except ConnectionFailure:
        print("Server not available")
    # Limpiado tablas e indices con pymongo
    for collname in db.collection_names():
        coll = Collection(db, name=collname)
        coll.drop()
        # coll_drop.indexes()

    client.close()


def borrarindicesevitardups():
    # Conexion a local
    client = MongoClient()
    
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        db = Database(client=client,
                      name=ConfiguracionGlobal.MONGODB)
    except ConnectionFailure:
        print("Server not available")
    # Limpiado tablas e indices con pymongo
    for collname in db.collection_names():
        coll = Collection(db, name=collname)
        coll.drop_indexes()
    
    client.close()
