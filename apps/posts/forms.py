from wtforms_tornado import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email



class CategoryForm(Form):
    name = StringField('分类名', validators=[
        DataRequired(message='请输入分类名'),
        Length(1, 50)
    ])

    desc = StringField('分类描述', validators=[
        DataRequired(message='请输入分类描述'),
        Length(1, 250)
    ])


class PostForm(Form):
    title = StringField('文章标题', validators=[
        DataRequired(message='请输入标题'),
        Length(1, 50)
    ])

    content = TextAreaField('文章内容', validators=[
        DataRequired(message='请输入文章内容'),
    ])

    category = StringField('文章分类', validators=[
        DataRequired(message='请输入分类'),
        Length(1, 50)
    ])

    is_top = BooleanField('文章是否置顶')
