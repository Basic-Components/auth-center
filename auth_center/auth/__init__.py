"""用于提供给前端直接访问获取登录token或者注册用户的模块
"""
import uuid
import asyncio
import aiohttp
import datetime
from sanic import Blueprint
from sanic.response import json, html
from sanic_redis import Namespace
from sanic_cors import cross_origin
from auth_center.model import User, Role
from auth_center.decorator import captcha_check, authorized
from .login_ip import ip_save
auth = Blueprint('auth')


@auth.post("/")
async def auth_index(request):
    namespace = Namespace(request.app.name + "-auth_token")
    json_data = request.json
    username = json_data.get("username")
    password = json_data.get("password")
    remember = json_data.get("remember")
    try:
        user = await User.get(User.username == username)
    except Exception as e:
        return json({"message": "用户不存在"}, 401)
    else:
        re = await request.app.redis["auth_token"].get(namespace(str(user._id)))

        if re:
            await ip_save(request,user)
            return json({"message": re.decode("utf-8"),"warn":"用户已经有激活的token"})
        flag = user.password.check_password(password)
        if flag:
            roles = [i.service_name for i in await user.roles]
            token_dic = {
                "_id": str(user._id),
                "roles": roles
            }
            token = request.app.serializer.dumps(token_dic)
            await request.app.redis["auth_token"].set(namespace(str(user._id)), token)
            if remember:
                await request.app.redis["auth_token"].expire(namespace(str(user._id)),
                                                request.app.config["TOKEN_REMEMBER_LIFECYCLE"])
            else:
                await request.app.redis["auth_token"].expire(namespace(str(user._id)),
                                                request.app.config["TOKEN_LIFECYCLE"])
            await ip_save(request,user)
            return json({"message": token})
        else:
            return json({"message": "密码不正确"}, 401)

@auth.post("/logout")
@authorized()
async def auth_logout(request):
    """注销,需要headers上有Authorization
    """
    namespace = Namespace(request.app.name + "-auth_token")
    try:
        re = await request.app.redis["auth_token"].delete(
                        namespace(request.args['auth_id']))
    except Exception as e:
        return json({"message": "redis操作错误", "error": str(e)}, 500)
    else:
        return json({"message":"ok"})



@auth.post("/signup")
@captcha_check("signup")
async def auth_signup(request):
    """为User表添加新的成员,传入的必须为一个名为users的列表,
    元素包含username和password和main_email
    """
    namespace = Namespace(request.app.name + "-captcha-signup")
    json_data = request.json
    username = json_data.get("username")
    password = json_data.get("password")
    main_email = json_data.get("main_email")

    try:
        user_count = await User.select().where(User.username == username).count()
    except Exception as e:
        return json({"message": "数据库操作错误", "error": str(e)}, 500)

    if user_count > 0:
        return json({"message": "用户名已存在"}, 401)

    try:
        user_count = await User.select().where(User.main_email == main_email).count()
    except Exception as e:
        return json({"message": "数据库操作错误", "error": str(e)}, 500)
    if user_count > 0:
        return json({"message": "email已被注册"}, 401)

    iq = User.insert_many([{"_id": uuid.uuid4(),
                            "username": username,
                            'password': username,
                            "main_email": main_email,
                            "ctime":datetime.datetime.now()
                            }])
    try:
        result = await iq.execute()
    except Exception as e:
        return json({"message": "数据库操作错误", "error": str(e)}, 500)

    else:
        if result:
            return json({
                "result": True
            })
        else:
            return json({
                "result": False
            })


@auth.post("/signup/ajax/username")
async def auth_signup_ajax_username(request):
    try:
        username = request.json["username"]
    except:
        return json({"message":"需要有`username字段`"},500)
    try:
        user_count = await User.select().where(User.username == username).count()
    except Exception as e:
        return json({"message": "数据库操作错误", "error": str(e)}, 500)
    if user_count > 0:
        return json({"message": "用户已存在", "result": False})
    else:
        return json({"message": "用户名可用", "result": True})


@auth.post("/signup/ajax/main_email")
async def auth_signup_ajax_username(request):
    try:
        main_email = request.json["main_email"]
    except:
        return json({"message":"需要有`main_email`字段"},500)
    try:
        user_count = await User.select().where(User.main_email == main_email).count()
    except Exception as e:
        return json({"message": "数据库操作错误", "error": str(e)}, 500)
    if user_count > 0:
        return json({"message": "email已被注册", "result": False})
    else:
        return json({"message": "email可用", "result": True})
