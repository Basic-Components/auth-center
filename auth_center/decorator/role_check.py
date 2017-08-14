from functools import wraps
from sanic.response import json

def role_check():
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            if (request.app.name not in request.args['auth_roles']):
                return json({"message":"没有权限查看"},401)
            else:
                return await func(request, *args, **kwargs)
        return handler
    return decorator
