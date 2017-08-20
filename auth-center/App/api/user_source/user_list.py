"""
操作User这张表,可以查看,添加或者删除一条记录,修改需要对应的其他resource
"""
import uuid
import datetime
import peewee
from sanic.views import HTTPMethodView
from sanic.response import json
from App.model import User, Role
from App.decorator import authorized, role_check


class UserListSource(HTTPMethodView):
    """操作User这张表
    """
    decorators = [role_check(),authorized()]

    async def get(self, request):
        """直接查看User中的全部内容,可以添加参数name查看username为name的用户是否存在
        """
        name = request.args.get("name")
        if name:
            try:
                user = await User.get(User.username == name)
            except:
                return json({"message":"找不到用户"},400)

            else:
                users = [user]
        else:
            users = await User.select()
        return json({"userlist": [
            {"_id": str(user._id),
             "username": user.username,
             "main_email":user.main_email,
             "roles": [i.service_name for i in await user.roles]} for user in users]
        })

    async def post(self, request):
        """为User表批量添加新的成员,使用inser_many,传入的必须为一个名为users的列表,每个元素包含username和password和main_email
        """
        try:
            request.json["users"]
        except:
            return json({"message":"需要传入一个名为users的列表,每个元素包含username和password和main_email"},500)
        iq = User.insert_many([{"_id": uuid.uuid4(),
                                "username": i["username"],
                                'password':i['password'],
                                "main_email":i['main_email'],
                                "ctime":datetime.datetime.now()
                                } for i in request.json["users"]])
        try:
            result = await iq.execute()
        except peewee.IntegrityError as pe:
            return json({"message":"用户数据已存在"},400)
        except Exception as e:
            return json({"message":"数据库错误","error":str(e)},500)
        else:
            if result:
                return json({
                    "result": True
                })
            else:
                return json({
                    "result": False
                })

    async def delete(self, request):
        """在User表中删除_id在users的用户,users传入的是一串_id列表
        """
        try:
            _ids = request.json["users"]
        except:
            return json({"message":"需要传入一个名为users的列表,每个元素为user的_id"},400)
        dq = User.delete().where(User._id << _ids)
        try:
            result = await dq.execute()
            print(result)
        except Exception as e:
            return json({"message":"数据库错误","error":str(e)},500)
        else:
            if result:
                return json({
                    "result": True
                })
            else:
                return json({
                    "result": False
                })
