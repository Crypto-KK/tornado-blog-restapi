from blog.models import BaseModel
from peewee import *

from apps.users.models import UserProfile
from blog.settings import settings

class Category(BaseModel):
    name = CharField(max_length=50, verbose_name='分类名')
    desc = CharField(max_length=250, verbose_name='分类详情')
    nums = IntegerField(default=0, verbose_name='分类文章数')


class Post(BaseModel):
    title = CharField(max_length=50, verbose_name='标题')
    author = ForeignKeyField(UserProfile, related_name='posts', on_delete='CASCADE', verbose_name='作者')
    category = ForeignKeyField(Category, related_name='all_posts', on_delete='CASCADE', verbose_name='文章分类')
    content = TextField(verbose_name='内容')

    like_nums = IntegerField(default=0, verbose_name='点赞数')
    read_nums = IntegerField(default=0, verbose_name='阅读数')
    comment_nums = IntegerField(default=0, verbose_name='评论数')

    is_excellent = BooleanField(default=False, verbose_name='是否精华')
    is_hot = BooleanField(default=False, verbose_name='是否热门')
    is_top = BooleanField(default=False, verbose_name='是否置顶')

    @classmethod
    def extend(cls):
        return cls.select(cls, UserProfile.id, UserProfile.username).join(
            UserProfile
        )