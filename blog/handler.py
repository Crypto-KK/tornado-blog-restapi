from tornado.web import RequestHandler
import redis

class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis()

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Credentials', "true")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Authorization, Access-Control-Allow-Origin, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')


