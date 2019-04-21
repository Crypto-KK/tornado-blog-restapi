import json
import uuid
import aiofiles
import jwt

from playhouse.shortcuts import model_to_dict
from blog.handler import BaseHandler
from blog.settings import settings
from .models import Post, Category
from .forms import CategoryForm
from utils import utils
from utils.decorators import authenticated_async


class CategoryHandler(BaseHandler):
    '''
    获取所有分类
    get -> /categories/

    新增分类（登录）
    post -> /categories/
    payload:
        {
            "name": "分类名"
            "desc": "分类描述
        }

    '''

    async def get(self, *args, **kwargs):
        res = {}
        MAX_PER_PAGE = settings["MAX_PER_PAGE"]
        query = Category.select().order_by(Category.add_time.desc())
        count = await self.application.objects.count(query)
        page = 0
        if count > MAX_PER_PAGE:
            page = count // MAX_PER_PAGE
            if count % MAX_PER_PAGE:
                rest = count - page * MAX_PER_PAGE
                page += 1

            else:
                rest = MAX_PER_PAGE
        else:
            rest = count

        '''
            count: 总查询记录
            page：总页数
            rest：最后一页的记录数
        '''
        print(count, page, rest)
        self.finish(res)

    @authenticated_async()
    async def post(self, *args, **kwargs):
        res = {}
        try:
            data = self.request.body.decode('utf-8')
            data = json.loads(data)
            form = CategoryForm.from_json(data)
        except json.decoder.JSONDecodeError:
            res['detail'] = '传入参数出错！'
            self.set_status(400)
            self.finish(res)
            return

        if form.validate():
            name = form.name.data
            desc = form.desc.data
            query = Category.select().where(Category.name==name)
            count = await self.application.objects.count(query)
            if count:
                res['name'] = '分类名重复！请重新输入'
                self.set_status(400)
            else:
                category = await self.application.objects.create(
                    Category,
                    name=name,
                    desc=desc
                )
                res = model_to_dict(category)
                self.set_status(201)

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field][0]

        self.finish(json.dumps(res, default=utils.json_serial))




class CategoryDetailHandler(BaseHandler):
    '''
    获取id=id的分类详情
    get -> /categories/{id}

    更改分类（登录）
    put -> /categories/{id}/
    payload:
        {
            "name": "分类名"
            "desc": "分类描述
        }

    删除分类（管理员required）
    delete -> /categories/{id}/
    '''

    async def get(self, category_id, *args, **kwargs):
        res = {}
        try:
            category = await self.application.objects.get(
                Category,
                id=int(category_id)
            )
            res = model_to_dict(category)


        except Category.DoesNotExist as e:
            self.set_status(404)
            res['detail'] = '未找到。'

        self.finish(json.dumps(res, default=utils.json_serial))

    @authenticated_async()
    async def put(self, category_id, *args, **kwargs):
        res = {}
        data, form = None, None
        try:
            data = self.request.body.decode('utf-8')
            data = json.loads(data)
            form = CategoryForm.from_json(data)
        except json.decoder.JSONDecodeError:
            res['detail'] = '传入参数出错！'
            self.set_status(400)
            self.finish(res)
            return

        if form.validate():
            name = form.name.data
            desc = form.desc.data

            try:
                category = await self.application.objects.get(
                    Category,
                    id=int(category_id)
                )

                query = Category.select().where(Category.name==name)
                count = await self.application.objects.count(query)

                #排除分类名和自身的分类名相同
                if name == category.name:
                    count -= 1
                #分类名和其他重复
                if count:
                    res['name'] = '分类名重复！请重新输入'
                    self.set_status(400)

                else:
                    category.name = name
                    category.desc = desc
                    await self.application.objects.update(category)
                    res = model_to_dict(category)

            except Category.DoesNotExist:
                res['detail'] = '未找到对应的分类。'
                self.set_status(404)

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field][0]

        self.finish(json.dumps(res, default=utils.json_serial))

    @authenticated_async(verify_is_admin=True)
    async def delete(self, category_id, *args, **kwargs):
        res = {}
        try:
            category = await self.application.objects.get(
                Category,
                id=int(category_id)
            )

            await self.application.objects.delete(category)
            self.set_status(200)
            res['detail'] = '删除分类成功'

        except Category.DoesNotExist:
            res['detail'] = '未找到对应的分类。'
            self.set_status(404)

        self.finish(res)