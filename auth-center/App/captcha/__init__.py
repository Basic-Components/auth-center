import uuid
import json as ujson
from sanic import Blueprint
from sanic.response import json
from sanic_redis import Namespace
from .captcha_gen import gene_code

captcha = Blueprint('captcha')


@captcha.post("/")
async def captcha_index(request):
    try:
        _type = request.json["type"]
    except:
        return json({"message": "请求需要有`type`字段"},400)
    namespace = Namespace(request.app.name + "-captcha"+"-"+_type)
    id_ = uuid.uuid4()

    await request.app.ZMQ_Sockets["captcha-gene"].send(ujson.dumps({
        "method": "img_code"
    }).encode("utf-8"))

    message = await request.app.ZMQ_Sockets["captcha-gene"].recv()
    msg = ujson.loads(message.decode("utf-8"))
    print(msg)
    if msg["code"] != 200:
        return json({"message": "生成验证码失败"} ,500)
    else:
        b = msg["message"]["img"]
        text = msg["message"]["text"]
        await request.app.redis["captcha"].set(namespace(str(id_)), text)
        # 设置验证的存活时间
        await request.app.redis["captcha"].expire(namespace(str(id_)),
                                request.app.config["CAPTCHA_LIFECYCLE"])
        return json({"message": {'captcha_id': str(id_), 'content': b}})
