from functools import wraps

import jwt
from apps.users.models import UserProfile

res = {'detail': '身份认证信息未提供。'}
res_format = {'detail': '身份认证信息填写不正确，格式为：JWT token。'}
res_owner = {'detail': '需要拥有者权限。'}
def authenticated_async(verify_is_admin=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            Authorization = self.request.headers.get(
                'Authorization', None
            )
            try:
                Authorization = Authorization.split(' ')
                if len(Authorization) != 2:
                    self.set_status(401)
                    self.finish(res_format)
                    return None
                else:
                    if Authorization[0] != 'JWT':
                        self.set_status(401)
                        self.finish(res_format)
                        return None
            except Exception as e:
                self.set_status(401)
                self.finish(res)

            Authorization = Authorization[1]

            if Authorization:

                try:
                    data = jwt.decode(
                        Authorization,
                        self.settings['secret_key'],
                        leeway=self.settings['jwt_expire'],
                        options={"verify_exp": True}
                    )

                    user_id = data['id']

                    try:
                        user = await self.application.objects.get(
                            UserProfile,
                            id=user_id
                        )
                        if verify_is_admin:
                            if not user.is_admin:
                                self.set_status(401)
                                self.finish({'detail': '需要管理员权限。'})
                                return
                        self._current_user = user
                        await func(self, *args, **kwargs)
                    except UserProfile.DoesNotExist:
                        self.set_status(401)
                        self.finish(res)


                except jwt.exceptions.ExpiredSignatureError as e:
                    self.set_status(401)
                    self.finish(res)
                except jwt.exceptions.DecodeError as e:
                    self.set_status(401)
                    self.finish(res)
            else:
                self.set_status(401)
                self.finish({})

        return wrapper
    return decorator


def owner_required(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):

        user = self._current_user

        await func(self, *args, **kwargs)


    return wrapper