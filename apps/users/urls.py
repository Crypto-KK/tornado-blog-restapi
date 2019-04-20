from tornado.web import url
from apps.users.handler import CodeHandler, RegisterHandler, LoginHandler, UserHandler

urlpatterns = [
    url('/code/', CodeHandler),
    url('/register/', RegisterHandler),
    url('/login/', LoginHandler),
    url('/user/', UserHandler),
]
