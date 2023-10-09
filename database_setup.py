import os

import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')


def connect():
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host=os.getenv('HOST'),
            port=os.getenv('PORT'),
            database=os.getenv('DATABASE'),
            user=os.getenv('USER'),
            password=os.getenv('DB_PASSWORD'),
        )
        print('Connected')
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None


def close_connection(conn):
    if conn is not None:
        conn.close()
        print('Database connection closed.')


def create_orders_table():
    conn = connect()
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS orders
    (
        order_id      SERIAL PRIMARY KEY,
        user_id       INT  NOT NULL,
        products      VARCHAR NOT NULL,
        contact_name  VARCHAR NOT NULL,
        contact_phone VARCHAR NOT NULL
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    close_connection(conn)


def main():
    conn = connect()
    if conn is not None:
        close_connection(conn)


if __name__ == '__main__':
    main()
