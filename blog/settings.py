import peewee_async
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = {
    "MEDIA_ROOT": os.path.join(BASE_DIR, "media"),
    "secret_key": "d#aPr8%mssTZgVGy",
    "jwt_expire": 7*24*3600,
    "SITE_URL": "http://127.0.0.1:8888",
    'MAX_PER_PAGE': 10,
    'db': {
        "host": "127.0.0.1",
        "users": "root",
        "password": "998219",
        "name": "blog_tornado",
        "port": 3306
    },
    'redis': {

    }
}

db = peewee_async.MySQLDatabase(
    database=settings['db']['name'],
    host=settings['db']['host'],
    port=settings['db']['port'],
    user=settings['db']['users'],
    password=settings['db']['password'],
)