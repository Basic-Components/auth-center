from sanic_aioorm import AioOrm
from sanic_aioorm import AioModel as Model
from aioorm import AioManyToManyField as ManyToManyField
from peewee import CharField, UUIDField, DateTimeField, IntegerField, ForeignKeyField
from peewee import Proxy
from playhouse.fields import PasswordField

db = Proxy()


class BaseModel(Model):
    class Meta:
        database = db


@AioOrm.regist
class Role(BaseModel):
    service_name = CharField(max_length=64)

    def __unicode__(self):
        return self.service_name


@AioOrm.regist
class User(BaseModel):
    _id = UUIDField(primary_key=True)
    username = CharField(max_length=80, unique=True)
    password = PasswordField()
    main_email = CharField(max_length=80, unique=True)
    ctime = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    roles = ManyToManyField(Role, related_name='users')

    def __unicode__(self):
        return self.username


NoteUserThrough = User.roles.get_through_model()
AioOrm.regist(NoteUserThrough)


@AioOrm.regist
class IP(BaseModel):
    ip = CharField()
    count = IntegerField(default=0)
    user = ForeignKeyField(User, related_name='ips')
    ctime = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    utime = DateTimeField(formats='%Y-%m-%d %H:%M:%S')


@AioOrm.regist
class UserAgents(BaseModel):
    content = CharField()
    ctime = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    utime = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    count = IntegerField(default=0)
    user = ForeignKeyField(User, related_name='agents')
