from functools import wraps
from sanic.response import json
from App.model import User
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

def role_or_self_check():
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            try:
                _id = kwargs["_id"]
            except:
                return json({"message":"url中需要有`_id`"},400)
            if not ((request.app.name in request.args['auth_roles']) or _id == request.args['auth_id']):
                return json({"message":"没有权限查看"},401)
            else:
                return await func(request, *args, **kwargs)
        return handler
    return decorator
