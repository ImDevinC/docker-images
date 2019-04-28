import logging
import sqlite3
from sqlite3 import Error
from yoyo import read_migrations
from yoyo import get_backend

class Database:
    def __init__(self, path):
        self.path = path
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.path)

    def do_migrations(self, migration_path):
        logging.debug(self.path)
        backend = get_backend('sqlite:///{}'.format(self.path))
        migrations = read_migrations(migration_path)
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

    def get_rows(self, query):
        if self.connection is None:
            self.connect()
        cur = self.connection.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    
    def execute_query(self, query):
        if self.connection is None:
            self.connect()
        cur = self.connection.cursor()
        cur.execute(query)
        self.connection.commit()
    
    def execute_query_list(self, queries):
        if self.connection is None:
            self.connect()
        cur = self.connection.cursor()
        for query in queries:
            logging.debug(query)
            cur.execute(query)
        self.connection.commit()

    def get_path(self):
        rows = self.get_rows('PRAGMA database_list;')
        for row in rows:
            print(row[0], row[1], row[2])

    def show_tables(self):
        rows = self.get_rows('SELECT name FROM sqlite_master WHERE type = \'table\' AND name NOT LIKE \'sqlite_%\';')
        for row in rows:
            logging.debug(row)

    def get_duplicate_items(self, table, hashes):
        return self.get_rows('SELECT hash, price FROM {} WHERE hash IN ({});'.format(table, hashes))

    def save_products_to_table(self, table, products):
        queries = []
        for product in products:
            details = products[product]
            if details['price-change'] == True:
                queries.append('UPDATE {} SET price = \'{}\' WHERE hash = \'{}\';'.format(table, details['price'], product))
            else:
                queries.append('INSERT INTO {} (hash, price) VALUES (\'{}\', \'{}\');'.format(table, product, details['price']))
        if len(queries) == 0:
            return
        self.execute_query_list(queries)