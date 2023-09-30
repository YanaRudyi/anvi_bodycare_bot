from product_details import get_product_page_links, parse_product_page
import psycopg2
import os

db_params = {
    'dbname': os.getenv('DATABASE'),
    'user': os.getenv('USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('HOST'),
    'port': os.getenv('PORT')
}

conn = psycopg2.connect(**db_params)

cur = conn.cursor()

create_table_query = '''
    CREATE TABLE IF NOT EXISTS product_details (
        id SERIAL PRIMARY KEY,
        product_name TEXT,
        description TEXT,
        prices TEXT[],
        weight_volume TEXT[]
    );
'''

cur.execute(create_table_query)
conn.commit()

shop_url = 'https://www.anvibodycare.com/shop'

product_page_links = get_product_page_links(shop_url)
product_details_list = []

for link in product_page_links:
    product_info = parse_product_page(link)
    product_details_list.append(product_info)

for product_info in product_details_list:
    print(product_info)
    insert_query = '''
        INSERT INTO product_details (product_name, description, prices, weight_volume)
        VALUES (%s, %s, %s, %s)
    '''

    cur.execute(insert_query, (
        product_info.get('product name', ''),
        product_info.get('description', ''),
        product_info.get('prices', []),
        product_info.get('weight_volume', []),
    ))

conn.commit()
cur.close()
conn.close()
