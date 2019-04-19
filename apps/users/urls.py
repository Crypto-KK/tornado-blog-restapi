from tornado.web import url
from apps.users.handler import CodeHandler, RegisterHandler

urlpatterns = [
    url('/code/', CodeHandler),
    url('/register/', RegisterHandler),
]
