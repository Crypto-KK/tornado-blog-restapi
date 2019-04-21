from tornado.web import url
from .handler import CategoryHandler, CategoryDetailHandler

urlpatterns = [
    url('/categories/', CategoryHandler),
    url('/categories/([0-9]{1,})/', CategoryDetailHandler),

]
