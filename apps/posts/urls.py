from tornado.web import url
from .handler import CategoryHandler, CategoryDetailHandler, \
    PostHandler, PostDetailHandler

urlpatterns = [
    url('/categories/', CategoryHandler),
    url('/categories/([0-9]{1,})/', CategoryDetailHandler),
    url('/posts/', PostHandler),
    url('/posts/([0-9]{1,})/', PostDetailHandler),

]
