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


def create_table(conn):
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS question (id serial PRIMARY KEY, name varchar, phone_number varchar, "
            "question varchar);")
        conn.commit()
        cur.close()
        print('Table "question" created successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating table: {error}")


def main():
    conn = connect()
    if conn is not None:
        create_table(conn)
        close_connection(conn)


if __name__ == '__main__':
    main()
