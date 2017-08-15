from functools import wraps
from sanic.response import json
from sanic_redis import Namespace
from auth_center.model import User

def captcha_check(_type):
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            json_data = request.json
            if request.method == "GET":
                return await func(request, *args, **kwargs)
            else:
                captcha_id = json_data.get("captcha_id")
                captcha_code = json_data.get("captcha_code")
                if not all([captcha_id,captcha_code]):
                    return json({"message":"传入的json中需要有字段captcha_id,captcha_code"},400)
                else:
                    captcha_code = captcha_code.encode("utf-8")
                    namespace = Namespace(request.app.name + "-captcha"+"-"+_type)
                    code = await request.app.redis["captcha"].get(namespace(captcha_id))
                    if code is None:
                        return json({"message": "找不到验证码信息,可能已过期"}, 401)
                    else:
                        if code != captcha_code:
                            return json({"message": "验证码错误"}, 401)
                        else:
                            return await func(request, *args, **kwargs)
        return handler
    return decorator
