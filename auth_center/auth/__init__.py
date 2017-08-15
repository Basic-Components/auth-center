"""用于提供给前端直接访问获取登录token或者注册用户的模块
"""
import uuid
import asyncio
import aiohttp
import base64
from io import BytesIO
from sanic import Blueprint
from sanic.response import json, html
from sanic_redis import Namespace
from sanic_cors import cross_origin
from auth_center.model import User, Role
from auth_center.decorator import captcha_check
from .captcha_gen import gene_code
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
        print(re)
        if re:
            return json({"message": "用户已经有激活的token"}, 401)
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

            return json({"message": token})
        else:
            return json({"message": "密码不正确"}, 401)


@auth.post("/captcha")
async def auth_captcha(request):
    try:
        _type = request.json["type"]
    except:
        return json({"message":"请求需要有`type`字段"},400)
    if _type not in ("signup","password","email","role"):
        return json({"message":'请求`type`字段只能在"signup","password","email","role"之中'},400)
    namespace = Namespace(request.app.name + "-captcha"+"-"+_type)
    id_ = uuid.uuid4()
    loop = asyncio.get_event_loop()
    img, text = await loop.run_in_executor(None,gene_code,request.app)
    await request.app.redis["captcha"].set(namespace(str(id_)), text)
    # 设置验证的存活时间
    await request.app.redis["captcha"].expire(namespace(str(id_)), request.app.config["CAPTCHA_LIFECYCLE"])
    with BytesIO() as f:
        img.save(f, 'png')
        b = base64.b64encode(f.getvalue())
    return json({"message": {'captcha_id': str(id_), 'content': b}})


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
    #captcha_id = json_data.get("captcha_id")
    #captcha_code = json_data.get("captcha_code").encode("utf-8")
    # code = await request.app.redis["captcha"].get(namespace(captcha_id))
    # if code is None:
    #     return json({"message": "找不到验证码信息,可能已过期"}, 401)
    # else:
    #     if code != captcha_code:
    #         return json({"message": "验证码错误"}, 401)
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
                            "main_email": main_email
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
