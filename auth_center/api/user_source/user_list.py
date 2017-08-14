"""
操作User这张表,可以查看,添加或者删除一条记录,修改需要对应的其他resource
"""

from sanic.views import HTTPMethodView
from sanic.response import json
from auth_center.model import User, Role
from auth_center.decorator.auth_check import authorized


class UserListSource(HTTPMethodView):
    """操作User这张表
    """

    @authorized()
    async def get(self, request):
        """直接查看User中的全部内容,可以添加参数name查看username为name的用户是否存在
        """
        if (request.app.name not in request.args['_roles']):
            return json({"message":"you do not have permission to see other's infomation"},401)

        else:
            name = request.args.get("name")
            if name:
                try:
                    user = await User.get(User.username == name)
                except:
                    return json({"message":"can not find the user"},401)

                else:
                    users = [user]
            else:
                users = await User.select()
            return json({"userlist": [
                {"_id": str(user._id),
                 "username": user.username,
                 "main_email":user.main_email,
                 "roles": [i.rolename for i in await user.roles]} for user in users]
            })

    async def post(self, request):
        """为User表添加新的成员,使用inser_many,传入的必须为一个名为users的列表,每个元素包含username和password和main_email
        """
        if (request.app.name not in request.args['_roles']):
            return json({"message":"you do not have permission to see other's infomation"},401)

        else:
            iq = User.insert_many([{"_id": uuid.uuid4(),
                                    "username": i["username"],
                                    'password':i['password'],
                                    "main_email":i['main_email']
                                    } for i in request.json["users"]])
            try:
                result = await iq.execute()
            except Exception as e:
                return json({"message":e.message},500)

            else:
                if result:
                    return json({
                        "result": True
                    })
                else:
                    return json({
                        "result": False
                    })
    @authorized()
    async def delete(self, request):
        """在User表中删除username为name的用户
        """
        if (request.app.name not in request.args['_roles']):
            return json({"message":"you do not have permission to delete other's infomation"},401)
        else:
            name = request.json["name"]
            dq = User.delete().where(User.username == name)
            try:
                nr = await dq
            except Exception as e:
                return json({"message":e.message},500)

            else:
                if result:
                    return json({
                        "result": True
                    })
                else:
                    return json({
                        "result": False
                    })
