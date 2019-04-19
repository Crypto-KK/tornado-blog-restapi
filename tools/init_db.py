
from peewee import MySQLDatabase
from apps.users.models import UserProfile, VerifyEmailCode

db = MySQLDatabase(
    'blog_tornado', host='127.0.0.1',port=3306,user='root',password='998219'
)
def init():
    #生成表
    db.create_tables([VerifyEmailCode])

if __name__ == '__main__':
    init()