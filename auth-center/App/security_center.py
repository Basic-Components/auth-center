"""
用户中心服务
"""

import random
import asyncio
import aiohttp

from sanic import Blueprint
from sanic.response import json,html

from sanic_cors import CORS

from App.model import User, Role
from App.decorator.auth_check import authorized

security_center = Blueprint('security_center')

CORS(security_center,automatic_options=True)

@security_center.post("/change_email")
@authorized()
async def auth_change_email(request):
    json_data = request.json
    username = json_data.get("username")
    password = json_data.get("password")
    main_email = json_data.get("main_email")
    new_email = json_data.get("new_email")
    try:
        user = await User.get(User.username == username)
    except Exception as e:
        raise SourceNotFound("UserDoesNotExist")
    else:
        flag = user.password.check_password(password) and \
                username == request.args['_username'] and \
                main_email==user.main_email and \
                new_email !=main_email
        if flag:
            token_dic = {
                "_id":str(user._id),
                "source":"UserEmailSource",
                "new_email":new_email
            }
            token = request.app.serializer.dumps(token_dic)
            return json({"status":200,"message":token})
        else:
            raise SourceNotFound("user and token not match")

@security_center.route("/change_password", methods=['POST', 'OPTIONS'])
@cross_origin(auth)
@authorized()
async def auth_change_email(request):
    json_data = request.json
    username = json_data.get("username")
    password = json_data.get("password")
    new_password = json_data.get("new_password")
    try:
        user = await User.get(User.username == username)
    except Exception as e:
        raise SourceNotFound("UserDoesNotExist")
    else:
        flag = user.password.check_password(password) and \
                username == request.args['_username'] and \
                password != new_password
        if flag:
            token_dic = {
                "_id":str(user._id),
                "source":"UserPasswordSource",
                "new_password":new_password
            }
            token = request.app.serializer.dumps(token_dic)
            return json({"status":200,"message":token})
        else:
            raise SourceNotFound("user and token not match")

@security_center.get("/password_lost/<token>")
async def auth_password_lost_verify(request,token):
    try:
        token_info = request.app.serializer.loads(token,request.app.config['TOKEN_TIME'])
    except SignatureExpired as e:
        raise SourceNotFound("token is out of date")
    source = token_info["source"]
    now_id = token_info["_id"]
    new_password = token_info["new_password"]
    try:
        user = await User.get(User._id == now_id)
    except:
        raise SourceNotFound("can not find the user")
    if source != "UserPasswordSource":
        raise SourceNotFound("you do not have permission to update password")
    else:
        try:
            user.password = new_password
            result = await user.save()
        except Exception as e:
            print(e)
            return html('<p>Dear {username}! password save failed!</p>'.format(username=user.username))
        else:
            return html('''<p>Dear {username}! password save succeed ,remember your new password {password}!</p>
                        '''.format(
                username=user.username,password=new_password
            ))

@security_center.route("/password_lost", methods=['POST', 'OPTIONS'])
@cross_origin(auth)
async def auth_password_lost(request):
    json_data = request.json
    username = json_data.get("username")
    main_email=json_data.get("main_email")
    try:
        user = await User.get(User.username == username)
    except Exception as e:
        raise SourceNotFound("UserDoesNotExist")
    else:
        flag = (username == request.args['_username']) and \
                user.main_email == main_email
        if flag:
            new_password = "".join(random.sample('ASDFGHJKLQWERTYUIOPZXCVBNMasdfghjklqwertyuiopzxcvbnm1234567890_',8))
            token_dic = {
                "_id":str(user._id),
                "source":"UserPasswordSource",
                "new_password":new_password
            }
            token = request.app.serializer.dumps(token_dic)
            send_data = {
                "username":username,
                "email":main_email,
                "token":token,
                "new_password":new_password
            }
            loop = asyncio.get_event_loop()
            async with aiohttp.ClientSession(loop=loop) as client:
                 async with client.post('http://python.org',json=send_data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return json({"status":200,"message":"send email to your main email adress, please check"})
                    else:
                        print("send email error")
                        raise SourceNotFound("send email error")
        else:
            raise SourceNotFound("user and token not match")
