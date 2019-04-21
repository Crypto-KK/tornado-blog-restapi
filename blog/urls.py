from tornado.web import url
from tornado.web import StaticFileHandler
from blog.settings import settings
from apps.users import urls as user_urls
from apps.posts import urls as posts_urls

urlpatterns = [
    (url("/media/(.*)", StaticFileHandler, {"path": settings["MEDIA_ROOT"]}))
]

urlpatterns += user_urls.urlpatterns
urlpatterns += posts_urls.urlpatterns