from blog.settings import db
from peewee import *
from datetime import datetime

class BaseModel(Model):
    add_time = DateTimeField(default=datetime.now, verbose_name="添加时间", help_text='添加时间')
    update_time = DateTimeField(default=datetime.now, verbose_name='更新时间', help_text='更新时间')

    def save(self, *args, **kwargs):
        if self._get_pk_value() is None:
            self.add_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        self.update_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")

        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = db