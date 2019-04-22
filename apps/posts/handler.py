import json
import uuid
import aiofiles
import jwt

from playhouse.shortcuts import model_to_dict
from blog.handler import BaseHandler
from blog.settings import settings
from .models import Post, Category
from .forms import CategoryForm, PostForm
from utils import utils
from utils.decorators import authenticated_async, owner_required


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
        '''
            count: 总查询记录
            page：总页数
            rest：最后一页的记录数
            current_page: 当前页数
            current_base_url: 当前api地址
        '''
        res = {}
        MAX_PER_PAGE  = settings['MAX_PER_PAGE']
        PARAM = settings['PAGINATE_PARAM']
        current_page = self.get_argument(PARAM, default="1")
        try:
            current_page = int(current_page)
        except ValueError as e:
            self.set_status(404)
            res['detail'] = '传入参数错误'
            self.finish(res)
            return

        query = Category.select().order_by(Category.add_time.desc())
        count = await self.application.objects.count(query)
        page = utils.get_page(count)

        previous, next, err = utils.get_next_pre_page('/categories/', current_page, page)

        #page传入错误 无效
        if err:
            self.set_status(404)
            res['detail'] = err
            self.finish(res)
            return

        #查询数据库并进行分页
        query = Category.select().order_by(Category.add_time.desc()).paginate(current_page, MAX_PER_PAGE)
        categories = await self.application.objects.execute(query)
        results = []
        for category in categories:
            results.append(model_to_dict(category))

        res = {
            "count": str(count),
            "next": next,
            "previous": previous,
            "results": results
        }


        self.finish(json.dumps(res, default=utils.json_serial))

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


class PostHandler(BaseHandler):
    '''
    获取所有文章
    get -> /posts/

    新增分类（登录）
    post -> /posts/
    payload:
        {
            "title": "分类名"
            "content": "内容"
            "category": "分类"
            "is_top": "是否置顶"
        }

    '''

    async def get(self, *args, **kwargs):
        '''
            count: 总查询记录
            page：总页数
            rest：最后一页的记录数
            current_page: 当前页数
            current_base_url: 当前api地址
        '''
        res = {}
        MAX_PER_PAGE  = settings['MAX_PER_PAGE']
        PARAM = settings['PAGINATE_PARAM']
        current_page = self.get_argument(PARAM, default="1")
        try:
            current_page = int(current_page)
        except ValueError as e:
            self.set_status(404)
            res['detail'] = '传入参数错误'
            self.finish(res)
            return

        query = Post.select().order_by(Post.add_time.desc())
        count = await self.application.objects.count(query)
        page = utils.get_page(count)

        previous, next, err = utils.get_next_pre_page('/posts/', current_page, page)

        #page传入错误 无效
        if err:
            self.set_status(404)
            res['detail'] = err
            self.finish(res)
            return

        #查询数据库并进行分页

        query = Post.extend().order_by(Post.add_time.desc()).paginate(current_page, MAX_PER_PAGE)
        posts = await self.application.objects.execute(query)
        results = []
        for post in posts:
            item = {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "category": {
                        "id": post.category.id,
                        "name": post.category.name,
                        "desc": post.category.desc,
                    },
                    "author": {
                        "id": post.author.id,
                        "username": post.author.username,
                    },
                    "like_nums": post.like_nums,
                    "read_nums": post.read_nums,
                    "comment_nums": post.comment_nums,
                    "is_excellent": post.is_excellent,
                    "is_hot": post.is_hot,
                    "is_top": post.is_top,
                    "add_time": post.add_time,
                    "update_time": post.update_time,
                }
            results.append(item)

        res = {
            "count": str(count),
            "next": next,
            "previous": previous,
            "results": results
        }


        self.finish(json.dumps(res, default=utils.json_serial))

    @authenticated_async()
    async def post(self, *args, **kwargs):
        res = {}
        try:
            data = self.request.body.decode('utf-8')
            data = json.loads(data)
            form = PostForm.from_json(data)
        except json.decoder.JSONDecodeError:
            res['detail'] = '传入参数出错！'
            self.set_status(400)
            self.finish(res)
            return

        if form.validate():

            category_id = form.category.data
            category = await self.application.objects.get(
                Category,
                id=int(category_id)
            )

            post = await self.application.objects.create(
                Post,
                title=form.title.data,
                content=form.content.data,
                category=category,
                is_top=form.is_top.data,
                author=self._current_user
            )
            res = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "category": {
                    "id": post.category.id,
                    "name": post.category.name,
                    "desc": post.category.desc,
                },
                "author": {
                    "id": post.author.id,
                    "username": post.author.username,
                },
                "like_nums": post.like_nums,
                "read_nums": post.read_nums,
                "comment_nums": post.comment_nums,
                "is_excellent": post.is_excellent,
                "is_hot": post.is_hot,
                "is_top": post.is_top,
                "add_time": post.add_time,
                "update_time": post.update_time,
            }
            self.set_status(201)

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field][0]

        self.finish(json.dumps(res, default=utils.json_serial))



class PostDetailHandler(BaseHandler):
    '''
    获取id=id的文章详情
    get -> /posts/{id}

    更改文章（登录, 拥有者）
    put -> /posts/{id}/
    payload:
        {
            "title": "标题"
            "content": "内容
            "category": "分类id
            "is_top": "是否置顶
        }

    删除文章（登录，拥有者）
    delete -> /posts/{id}/
    '''

    async def get(self, post_id, *args, **kwargs):
        res = {}
        try:
            query = Post.extend().where(
                Post.id==int(post_id)
            )
            post = await self.application.objects.execute(query)
            try:
                post = post[0]
                print(post.title)
                res = {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "category": {
                        "id": post.category.id,
                        "name": post.category.name,
                        "desc": post.category.desc,
                    },
                    "author": {
                        "id": post.author.id,
                        "username": post.author.username,
                    },
                    "like_nums": post.like_nums,
                    "read_nums": post.read_nums,
                    "comment_nums": post.comment_nums,
                    "is_excellent": post.is_excellent,
                    "is_hot": post.is_hot,
                    "is_top": post.is_top,
                    "add_time": post.add_time,
                    "update_time": post.update_time,
                    }
            except IndexError as e:
                self.set_status(404)
                res['detail'] = '未找到。'

        except Category.DoesNotExist as e:
            self.set_status(404)
            res['detail'] = '未找到。'

        self.finish(json.dumps(res, default=utils.json_serial))


    @authenticated_async()
    @owner_required
    async def put(self, post_id, *args, **kwargs):
        res = {}
        try:
            data = self.request.body.decode('utf-8')
            data = json.loads(data)
            form = PostForm.from_json(data)
        except json.decoder.JSONDecodeError:
            res['detail'] = '传入参数出错！'
            self.set_status(400)
            self.finish(res)
            return

        if form.validate():
            try:
                #取出文章和分类
                query = Post.extend().where(
                    Post.id == int(post_id)
                )
                post = await self.application.objects.execute(query)
                post = post[0]

                #检测当前用户是否是该文章的作者，不是的话无权修改
                if post.author != self.current_user:
                    self.set_status(401)
                    res = {'detail': '需要拥有者权限。'}
                    self.finish(res)
                    return

                category = await self.application.objects.get(
                    Category,
                    id=(form.category.data)
                )
                post.title = form.title.data
                post.content = form.content.data
                post.category = category
                post.is_top = form.is_top.data
                await self.application.objects.update(post)
                res = {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "category": {
                        "id": post.category.id,
                        "name": post.category.name,
                        "desc": post.category.desc,
                    },
                    "author": {
                        "id": post.author.id,
                        "username": post.author.username,
                    },
                    "like_nums": post.like_nums,
                    "read_nums": post.read_nums,
                    "comment_nums": post.comment_nums,
                    "is_excellent": post.is_excellent,
                    "is_hot": post.is_hot,
                    "is_top": post.is_top,
                    "add_time": post.add_time,
                    "update_time": post.update_time,
                }

            except Post.DoesNotExist:
                res['detail'] = '未找到对应的文章。'
                self.set_status(404)

            except Category.DoesNotExist:
                res['detail'] = '未找到对应的分类。'
                self.set_status(404)

        else:
            self.set_status(400)
            for field in form.errors:
                res[field] = form.errors[field][0]

        self.finish(json.dumps(res, default=utils.json_serial))

    @authenticated_async()
    @owner_required
    async def delete(self, post_id, *args, **kwargs):
        res = {}
        try:
            query = Post.extend().where(
                Post.id == int(post_id)
            )
            post = await self.application.objects.execute(query)
            post = post[0]
            # 检测当前用户是否是该文章的作者，不是的话无权删除
            if post.author != self.current_user:
                self.set_status(401)
                res = {'detail': '需要拥有者权限。'}
                self.finish(res)
                return

            await self.application.objects.delete(post)
            self.set_status(200)
            res['detail'] = '删除文章成功'

        except Category.DoesNotExist:
            res['detail'] = '未找到对应的文章。'
            self.set_status(404)

        self.finish(res)