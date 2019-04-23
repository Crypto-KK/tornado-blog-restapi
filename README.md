# tornado-blog-restapi
利用tornado编写restful api实现高并发博客问答平台后端系统

数据库采用mysql，引擎采用peewee-async

缓存采用redis，但是没有用到异步redis的第三方库

## 登录方式
使用JSON Web token方式登录，用到第三方库：Pyjwt

请求头中加入：Authorization:JWT {token}

## 接口符合restful规范，和djangorestframework实现的效果类似
post -> /login/ 登录，返回token

get -> /posts/ 获取所有文章，自动分页

post -> /posts/ 登录状态下新增文章

get -> /posts/{id}/ 获取某篇文章的内容

put -> /posts/{id}/ 登录状态下修改文章内容

delete -> /posts/{id}/ 删除文章

...
