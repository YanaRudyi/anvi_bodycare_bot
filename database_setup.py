import os

import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')


def connect():
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None


def close_connection(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')


def main():
    conn = connect()
    if conn is not None:
        close_connection(conn)


if __name__ == '__main__':
    main()
