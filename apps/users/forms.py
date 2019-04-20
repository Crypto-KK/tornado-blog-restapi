from wtforms_tornado import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class CodeForm(Form):
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email()
    ])


class RegisterForm(Form):
    code = StringField('验证码', validators=[
        DataRequired(message='请输入验证码'),
        Length(min=6,max=6),
    ])

    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email()
    ])

    password1 = StringField('密码', validators=[
        DataRequired(message='请输入密码')
    ])

    password2 = StringField('确认密码', validators=[
        DataRequired(message='请再次输入密码')
    ])


class LoginForm(Form):
    username = StringField("用户名", validators=[DataRequired(message="请输入用户名或者邮箱!"),])
    password = StringField("密码", validators=[DataRequired(message="请输入密码!")])
