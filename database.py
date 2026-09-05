import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

with psycopg.connect(
    dbname = os.getenv('DB_NAME'),
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    host = os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT')
) as connection:

    with connection.cursor() as cursor:

        pass



