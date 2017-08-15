from functools import wraps
from sanic.response import json


def ip_blacklist():
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            try:
                blacklist = request.app.config["IP_BLACKLIST"]
            except:
                return await func(request, *args, **kwargs)
            else:
                if request.ip in blacklist:
                    return json({"message":"您的ip地址不在服务范围"},401)
                else:
                    return await func(request, *args, **kwargs)
        return handler
    return decorator

def ip_whitelist():
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            try:
                whitelist = request.app.config["IP_WHITELIST"]
            except:
                return await func(request, *args, **kwargs)
            else:
                if request.ip not in whitelist:
                    return json({"message":"您的ip地址不在服务范围"},401)
                else:
                    return await func(request, *args, **kwargs)
        return handler
    return decorator
