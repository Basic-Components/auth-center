from functools import wraps
from sanic.response import json
from sanic.exceptions import NotFound,Unauthorized
from auth_server.exception import SourceNotFound, DatabaseError
from auth_server.model import User,Role

def authorized():
    def decorator(func):
        @wraps(func)
        async def handler(request, *args, **kwargs):
            # Middleware goes here
            try:
                token = request.headers["Authorization"]
            except KeyError as ke:
                return json({"message":"do not have the auth token"},401)
            try:
                token_info = request.app.serializer.loads(token,request.app.config['TOKEN_TIME'])
            except SignatureExpired as e:
                return json({"message":"token is out of date"},401)
            else:
                username = token_info["username"]
                try:
                    nowuser = await User.get(User.username==username)
                except Exception as e:
                    return json({"message":"user in token not exist"},401)
                else:
                    request.args['_username'] = token_info["username"]
                    request.args['_roles'] = token_info["roles"]
                    return await func(request, *args, **kwargs)
        return handler
    return decorator
