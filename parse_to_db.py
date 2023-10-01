from product_details import get_product_page_links, parse_product_page
import psycopg2.extras
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
        weight_volume TEXT[],
        availability BOOLEAN
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
    select_query = "SELECT COUNT(*) FROM product_details WHERE product_name = %s"
    cur.execute(select_query, (product_info.get('product name', ''),))
    count = cur.fetchone()[0]

    if count == 0:
        insert_query = '''
            INSERT INTO product_details (product_name, description, prices, weight_volume, availability)
            VALUES (%s, %s, %s, %s, %s)
        '''

        cur.execute(insert_query, (
            product_info.get('product name', ''),
            product_info.get('description', ''),
            product_info.get('prices', []),
            product_info.get('weight_volume', []),
            True
        ))
    else:
        update_query = 'UPDATE product_details SET availability = TRUE WHERE product_name = %s'
        cur.execute(update_query, (product_info.get('product name', ''),))

conn.commit()

update_missing_query = '''
    UPDATE product_details 
    SET availability = FALSE 
    WHERE product_name NOT IN %s
'''

cur.execute(update_missing_query, (tuple([product_info.get('product name', '')
                                          for product_info in product_details_list]),))

conn.commit()

cur.close()
conn.close()
