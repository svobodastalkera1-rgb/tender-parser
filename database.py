import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        dbname = os.getenv('DB_NAME'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        host = os.getenv('DB_HOST'),
        port = os.getenv('DB_PORT')
    )

def save_data(results):

    query = """ INSERT INTO items(
                        title,
                        price,
                        currency,
                        availability,
                        partnumber,
                        url,
                        article,
                        specs,
                        title_bd,
                        shop
                    ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        
                    ON CONFLICT (partnumber, article) DO UPDATE SET 
                        price = EXCLUDED.price,
                        availability = EXCLUDED.availability,
                        shop = EXCLUDED.shop,
                        url = EXCLUDED.url; """

    with get_connection() as connection:
        with connection.cursor() as cursor:

            for result in results:
                
                values = (
                    getattr(result, 'title', None),
                    getattr(result, 'price', None),
                    getattr(result, 'currency', 'RUB'),
                    getattr(result, 'availability', None),
                    getattr(result, 'partnumber', None),
                    getattr(result, 'url', None),
                    getattr(result, 'article', None),
                    getattr(result, 'specs', None),
                    getattr(result, 'title_bd', None),
                    getattr(result, 'shop', None)
                )

                cursor.execute(query, values)

            connection.commit()

def get_item(partnumber, title):

    query = """ SELECT title, price, availability FROM items WHERE partnumber = %s OR title = %s; """ 

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (partnumber, title))
            return cursor.fetchall()






