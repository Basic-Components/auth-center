import uuid
import base64
import asyncio
from io import BytesIO
from sanic import Blueprint
from sanic.response import json, html
from sanic_redis import Namespace
from .captcha_gen import gene_code


captcha = Blueprint('captcha')

@captcha.post("/")
async def captcha_index(request):
    try:
        _type = request.json["type"]
    except:
        return json({"message":"请求需要有`type`字段"},400)
    namespace = Namespace(request.app.name + "-captcha"+"-"+_type)
    id_ = uuid.uuid4()
    loop = asyncio.get_event_loop()
    img, text = await loop.run_in_executor(None,gene_code,request.app)
    await request.app.redis["captcha"].set(namespace(str(id_)), text)
    # 设置验证的存活时间
    await request.app.redis["captcha"].expire(namespace(str(id_)),
                            request.app.config["CAPTCHA_LIFECYCLE"])
    with BytesIO() as f:
        img.save(f, 'png')
        b = base64.b64encode(f.getvalue())
    return json({"message": {'captcha_id': str(id_), 'content': b}})
