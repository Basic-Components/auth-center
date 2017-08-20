from functools import wraps
from sanic.response import json
from sanic_redis import Namespace
from App.model import User,Role

def authorized():
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            # Middleware goes here
            namespace = Namespace(request.app.name+"-auth_token")
            try:
                token = request.headers["Authorization"]
            except KeyError as ke:
                return json({"message":"没有验证token"},401)

            token_info = request.app.serializer.loads(token)
            try:
                nowuser = await User.get(User._id==token_info["_id"])
            except Exception as e:
                return json({"message":"token指向的用户不存在"},401)
            else:
                try:
                    value = await request.app.redis["auth_token"].get(namespace(token_info["_id"]))
                except Exception as e:
                    print("_________")
                    print(e.message)
                    return json({"message":"token已过期"},401)
                else:
                    if value != token.encode("utf-8"):
                        print(value)
                        print(token)
                        return json({"message":"token过期已更改"},401)
                    else:
                        request.args['auth_id'] = token_info["_id"]
                        request.args['auth_roles'] = token_info["roles"]
                        return await func(request, *args, **kwargs)
        return handler
    return decorator
