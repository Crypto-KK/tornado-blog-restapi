from wtforms_tornado import Form
from wtforms import StringField, TextAreaField
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
