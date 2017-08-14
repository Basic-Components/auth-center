"""
操作User这张表,可以查看,添加或者删除一条记录,修改需要对应的其他resource
"""

from sanic.views import HTTPMethodView
from sanic.response import json
from auth_center.model import User, Role
from auth_center.decorator import authorized, role_check


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
                return json({"message":"找不到用户"},401)

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

    async def delete(self, request):
        """在User表中删除username为name的用户
        """
        if (request.app.name not in request.args['auth_roles']):
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
