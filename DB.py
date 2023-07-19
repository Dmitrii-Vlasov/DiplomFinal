import psycopg2
from psycopg2 import sql


class DataBase:
    def __init__(self, db_url_object):
        self.conn = psycopg2.connect(db_url_object)
        self.cursor = self.conn.cursor()

    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                profile_id INTEGER,
                worksheet_id INTEGER
            )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert(self, profile_id, worksheet_id):
        insert_query = sql.SQL("INSERT INTO users (profile_id, worksheet_id) VALUES (%s, %s)")
        self.cursor.execute(insert_query, (profile_id, worksheet_id))
        self.conn.commit()

    def select(self):
        select_query = sql.SQL("SELECT profile_id, worksheet_id FROM users")
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
