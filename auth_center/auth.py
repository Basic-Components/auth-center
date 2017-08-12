import random
import asyncio
import aiohttp
from sanic_cors import cross_origin
from sanic import Blueprint
from sanic.response import json,html

from auth_center.model import User, Role
from auth_center.decorator.auth_check import authorized

auth = Blueprint('auth')


@auth.route("/", methods=['POST', 'OPTIONS'])
@cross_origin(auth)
async def auth_index(request):
    if request.method == "POST":
        print(request)
        json_data = request.json
        username = json_data.get("username")
        password = json_data.get("password")
        try:
            user = await User.get(User.username == username)
        except Exception as e:
            return josn({"message":"UserDoesNotExist"},401)
        else:
            flag = user.password.check_password(password)
            if flag:
                roles = [i.rolename for i in  await user.roles]
                token_dic = {
                    "username":username,
                    "roles":roles
                }
                token = request.app.serializer.dumps(token_dic)
                return json({"message":token})
            else:
                return josn({"message":"password not match"},401)
    else:
        return json("hello")
