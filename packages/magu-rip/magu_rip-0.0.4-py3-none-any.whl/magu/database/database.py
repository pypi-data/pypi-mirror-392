import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
#import mariadb
from magu import properties

class MySQLDatabase:
    @staticmethod
    def connect():
        try:
            conn = mysql.connector.connect(
                host=properties.DATABASE_HOST,
                user=properties.DATABASE_USER,
                password=properties.DATABASE_PASSWORD,
                port=properties.DATABASE_PORT,
                database=properties.DATABASE_NAME,
            )
            print(f"[DB] Connected with user {properties.DATABASE_USER} on host {properties.DATABASE_HOST}")
            conn.cursor().execute(f"USE {properties.DATABASE_NAME};")
            return conn
        except Error as e:
            print(f"[DB] ERROR: Couldn't connect to user {properties.DATABASE_USER} on host {properties.DATABASE_HOST}")
            return None
        
    @staticmethod
    @contextmanager
    def session():
        conn = MySQLDatabase.connect()
        if not conn or not conn.is_connected():
            raise ConnectionError("[DB] Couldn't create session")
        
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[DB] Query failed. Exception: {e}")
        finally:
            cursor.close()
            conn.close()

class MariaDBDatabase:
    @staticmethod
    def connect():
        try:
            conn = mariadb.connect(
                host=properties.DATABASE_HOST,
                user=properties.DATABASE_USER,
                password=properties.DATABASE_PASSWORD,
                port=properties.DATABASE_PORT,
                database=properties.DATABASE_NAME,
            )
            print(f"[DB] Connected with user {properties.DATABASE_USER} on host {properties.DATABASE_HOST}")
            conn.cursor().execute(f"USE `{properties.DATABASE_NAME}`;")
            return conn
        except Error as e:
            print(f"[DB] ERROR: Couldn't connect to user {properties.DATABASE_USER} on host {properties.DATABASE_HOST}")
            return None
        
    @staticmethod
    @contextmanager
    def session():
        conn = MariaDBDatabase.connect()
        if not conn:
            raise ConnectionError("[DB] Couldn't create session")
        
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("[DB] Query failed")
        finally:
            cursor.close()
            conn.close()
