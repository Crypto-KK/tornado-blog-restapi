import json
import uuid
import os
from datetime import datetime, timedelta
import random
import logging
import aiofiles
import jwt
from playhouse.shortcuts import model_to_dict
from blog.handler import BaseHandler
from apps.users.models import UserProfile, VerifyEmailCode
from apps.users.forms import CodeForm, RegisterForm, LoginForm
from utils import utils

class CodeHandler(BaseHandler):
    '''
    发送邮箱验证码
    post -> /code/
    payload:
        {
            "email": "邮箱"
        }
    '''
    def generate_code(self):
        '''
        生成六位数验证码保存在redis中
        '''
        seeds = '0123456789'
        code = []
        for i in range(6):
            code.append(random.choices(seeds)[0])
        return ''.join(code)

    async def post(self, *args, **kwargs):
        res = {}
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = CodeForm.from_json(data)
        if form.validate():
            email = form.email.data
            try:
                #验证该邮箱是否已被注册
                existed_user = await self.application.objects.get(UserProfile, email=email)
                self.set_status(400)
                res['email'] = '该邮箱已被注册'
            except UserProfile.DoesNotExist:
                one_min = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
                query = VerifyEmailCode.select().where(VerifyEmailCode.add_time>one_min)
                count = await self.application.objects.count(query)
                if count:
                    print('发送验证码间隔不能小于1分钟')
                    logging.log(logging.DEBUG, '发送验证码间隔不能小于1分钟')
                    res['email'] = '发送验证码间隔不能小于1分钟'
                else:

                    # 以string格式存入redis，10分钟过期
                    # self.redis_conn.set('{}_{}'.format(email, code), 1, 10*60)

                    # 验证码存入mysql，可选
                    code = self.generate_code()
                    await self.application.objects.create(
                        VerifyEmailCode,
                        code=code,
                        email=email
                    )

                    res['email'] = '验证码发送成功'
                    logging.log(logging.DEBUG, '{}-发送验证码成功'.format(email))
                    print('{}-发送验证码成功'.format(email))

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field]

        self.finish(res)


class RegisterHandler(BaseHandler):
    '''
    用户注册
    post -> /register/
    payload:
        {
            "email": "邮箱",
            "code": "验证码",
            "password1": "密码",
            "password2": "确认密码",
        }
    '''
    async def post(self, *args, **kwargs):
        res = {}
        data = self.request.body.decode('utf-8')
        data = json.loads(data)
        form = RegisterForm.from_json(data)
        if form.validate():
            email = form.email.data
            code = form.code.data
            password1 = form.password1.data
            password2 = form.password2.data

            #验证两次输入密码是否正确
            if password1 != password2:
                res['password1'] = '两次输入密码不一致'
                self.set_status(400)

            #验证验证码是否正确

            #redis方式验证
            #redis_key = "{}_{}".format(email, code)
            # if not self.redis_conn.get(redis_key):
            #     print('验证码错误')
            #     self.set_status(400)
            #     res['code'] = '验证码错误或者失效'


            #mysql方式验证(验证码5分钟内有效)
            try:
                #按照最新的时间顺序取出该邮箱对应的第一条验证码
                query = VerifyEmailCode.select().where(VerifyEmailCode.email==email).order_by(VerifyEmailCode.add_time.desc())
                qs = await self.application.objects.execute(query)
                five_mins = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)

                #5分钟有效期
                if five_mins > qs[0].add_time:
                    res['code'] = '验证码过期，请重新发送！'
                    self.set_status(400)

                #比对失败
                if qs[0].code != code:
                    res['code'] = '验证码错误！'
                    self.set_status(400)
                #比对成功
                else:
                    #创建用户，username置为email
                    user = await self.application.objects.create(
                        UserProfile,
                        email=email,
                        username=email,
                        password=password1
                    )
                    res = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'gender': user.gender,
                        'add_time': user.add_time #datetime不能直接用json序列化
                    }
                    self.set_status(201) #创建成功，201 CREATED

            except VerifyEmailCode.DoesNotExist:
                res['code'] = '请发送验证码'
                self.set_status(400)

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field]

        self.finish(json.dumps(res, default=utils.json_serial))


class LoginHandler(BaseHandler):
    '''
    用户登录
    post -> /login/
    payload:
        {
            "username": "用户名或者邮箱",
            "password": "密码"
        }
    '''
    async def post(self, *args, **kwargs):
        res = {}

        data = self.request.body.decode("utf-8")
        data = json.loads(data)
        form = LoginForm.from_json(data)
        if form.validate():
            username = form.username.data
            password = form.password.data
            try:
                query = UserProfile.select().where(
                    (UserProfile.username==username) | (UserProfile.email==username)
                )
                user = await self.application.objects.execute(query)
                user = user[0]
                if not user.password.check_password(password):
                    res['non_fields'] = '用户名或密码错误'
                    self.set_status(400)
                else:
                    payload = {
                        'id': user.id,
                        'username': username,
                        'exp': datetime.utcnow()
                    }
                    token = jwt.encode(payload, self.settings["secret_key"], algorithm='HS256')
                    res['token'] = token.decode('utf-8')

            except UserProfile.DoesNotExist:
                self.set_status(400)
                res['username'] = '用户不存在'

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field]

        self.finish(res)
