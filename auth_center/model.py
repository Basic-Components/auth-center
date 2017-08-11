from sanic_aioorm import AioOrm
from sanic_aioorm import AioModel as Model
from aioorm import AioManyToManyField as ManyToManyField
from peewee import CharField,UUIDField,Proxy
from playhouse.fields import PasswordField

db=Proxy()


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
    username = CharField(max_length=80, unique = True)
    password = PasswordField()
    main_email = CharField(max_length=80, unique = True)
    roles = ManyToManyField(Role, related_name='users')

    def __unicode__(self):
        return self.username
NoteUserThrough = User.roles.get_through_model()
AioOrm.regist(NoteUserThrough)
