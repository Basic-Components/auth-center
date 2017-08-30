import uuid
import datetime
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS
from sanic_redis import Redis
from sanic_aioorm import AioOrm
from itsdangerous import URLSafeTimedSerializer
import zmq
import zmq.asyncio
from App.model import db, User, Role
from App.auth import auth
from App.api import api
from App.captcha import captcha


def create_app(env):
    app = Sanic("auth-center")
    app.config.from_object(env)
    CORS(app, automatic_options=True)
    Redis(app)
    orm = AioOrm(app)
    orm.init_proxys(defaultdb=db)
    orm.create_tables(User=[{"_id": uuid.uuid4(),
                             "username": "admin",
                             "password": 'admin',
                             "main_email": "huangsizhe@rongshutong.com",
                             "ctime":datetime.datetime.now()
                             }
                            ],
                      Role=[{"service_name": app.name},
                            {"service_name": "msg_reverse_indexing"}])
    app.serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt=app.config['SALT'])
    app.blueprint(api, url_prefix='/api')
    app.blueprint(auth, url_prefix='/auth')
    app.blueprint(captcha, url_prefix='/captcha')

    @app.listener('after_server_start')
    async def creat_relationship(app, loop):
        realtionship_table = AioOrm._regist_classes['UserRoleThrough']
        if (await realtionship_table.select().count()) == 0:
            user = await User.get(User.username == "admin")
            roles = await Role.select()
            for role in roles:
                await user.roles.add(role)

    @app.listener('after_server_start')
    async def creat_zmq_client(app, loop):
        #zmq.asyncio.install()
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.REQ)
        print("Connecting to server...")
        socket.connect(app.config["ZMQ_URLS"]['captcha-gene'])
        app.ZMQ_Sockets = {}
        app.ZMQ_Sockets["captcha-gene"] = socket


    @app.get("/ping")
    async def ping(request):
        return json({"message":"pong"})
    return app
