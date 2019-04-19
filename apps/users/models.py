from blog.models import BaseModel
from peewee import *
from bcrypt import hashpw, gensalt


class PasswordHash(bytes):
    def check_password(self, password):
        password = password.encode('utf-8')
        return hashpw(password, self) == self


class PasswordField(BlobField):
    def __init__(self, iterations=12, *args, **kwargs):
        if None in (hashpw, gensalt):
            raise ValueError('Missing library required for PasswordField: bcrypt')
        self.bcrypt_iterations = iterations
        self.raw_password = None
        super(PasswordField, self).__init__(*args, **kwargs)

    def db_value(self, value):
        """Convert the python value for storage in the database."""
        if isinstance(value, PasswordHash):
            return bytes(value)

        if isinstance(value, str):
            value = value.encode('utf-8')
        salt = gensalt(self.bcrypt_iterations)
        return value if value is None else hashpw(value, salt)

    def python_value(self, value):
        """Convert the database value to a pythonic value."""
        if isinstance(value, str):
            value = value.encode('utf-8')

        return PasswordHash(value)


GENDERS = (
    ('female',"女生"),
    ('male',"男生"),
)

class UserProfile(BaseModel):
    username = CharField(max_length=150, unique=True, index=True, verbose_name='用户名')
    password = PasswordField(verbose_name="密码")
    email = CharField(max_length=50,  verbose_name='邮箱', help_text='邮箱')
    gender = CharField(max_length=10, choices=GENDERS, verbose_name='性别', help_text='性别', default='male')
    icon = CharField(max_length=200, null=True, verbose_name="头像")
    address = CharField(max_length=100, null=True, verbose_name="地址")
    bio = TextField(null=True, verbose_name="简介")
    birthday = DateField(null=True, verbose_name='出生日期', help_text='出生日期')

    follower_nums = IntegerField(default=0, verbose_name='关注的用户数量', help_text='关注的用户')
    followed_nums = IntegerField(default=0, verbose_name='粉丝数', help_text='粉丝数')

    is_valid = BooleanField(default=False, verbose_name='是否激活', help_text='是否激活')


class VerifyEmailCode(BaseModel):
    '''
    邮箱验证码
    '''
    code = CharField(max_length=6, verbose_name='验证码', help_text='验证码')
    email = CharField(max_length=50, verbose_name='邮箱', help_text='邮箱')

