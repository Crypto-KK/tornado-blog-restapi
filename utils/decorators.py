from functools import wraps

import jwt
from apps.users.models import UserProfile

def authenticated_async(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        Authorization = self.request.headers.get(
            'Authorization', None
        )
        try:
            Authorization = Authorization.split(' ')
            if len(Authorization) != 2:
                self.set_status(401)
                self.finish({'detail': '身份认证信息填写不正确，格式为：JWT token。'})
                return None
            else:
                if Authorization[0] != 'JWT':
                    self.set_status(401)
                    self.finish({'detail': '身份认证信息填写不正确，格式为：JWT token。'})

        except Exception as e:
            self.set_status(401)
            self.finish({'detail': '身份认证信息未提供。'})

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
                    self._current_user = user
                    await func(self, *args, **kwargs)
                except UserProfile.DoesNotExist:
                    self.set_status(401)
                    self.finish({'detail': '身份认证信息未提供。'})


            except jwt.exceptions.ExpiredSignatureError as e:
                self.set_status(401)
                self.finish({'detail': '身份认证信息未提供。'})
            except jwt.exceptions.DecodeError as e:
                self.set_status(401)
                self.finish({'detail': '身份认证信息未提供。'})
        else:
            self.set_status(401)
            self.finish({})

    return wrapper

