import uuid
from sanic import Sanic
from sanic import response
from sanic.response import json
from sanic_cors import CORS
from sanic_redis import Redis
from sanic_aioorm import AioOrm
from itsdangerous import URLSafeTimedSerializer
from auth_center.model import db, User, Role
from auth_center.auth import auth
from auth_center.api import api

app = Sanic("auth-center")
CORS(app,automatic_options=True)
#AioOrm.SetConfig(app, defaultdb="mysql://root:rstrst@localhost:3306/test_auth")
AioOrm.SetConfig(app, defaultdb="mysql://root:hsz881224@127.0.0.1:3306/test_auth")
orm = AioOrm(app)
orm.init_proxys(defaultdb=db)
orm.create_tables(User=[{"_id":uuid.uuid4(),
                         "username":"admin",
                         "password":'admin',
                         "main_email":"huangsizhe@rongshutong.com"}
                        ],
                  Role=[{"service_name":app.name},
                        {"service_name":"msg_reverse_indexing"}])

Redis.SetConfig(app, captcha="redis://localhost:6379/1",auth_token="redis://localhost:6379/2")
Redis(app)

app.config['SECRET_KEY'] = 'secret-key'
app.config['TOKEN_TIME'] = 3600
app.config['SALT']='sanic'
app.serializer=URLSafeTimedSerializer(app.config['SECRET_KEY'],salt=app.config['SALT'])

@app.listener('after_server_start')
async def creat_relationship(app, loop):
    realtionship_table = AioOrm._regist_classes['UserRoleThrough']
    if (await realtionship_table.select().count()) == 0:
        user = await User.get(User.username == "admin")
        roles = await Role.select()
        for role in roles:
            await user.roles.add(role)

app.blueprint(api,url_prefix='/api')
app.blueprint(auth,url_prefix='/auth')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4500)
